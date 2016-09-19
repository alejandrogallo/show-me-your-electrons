
def MOS_ASYMPTOTE(states, LB="17.2450", VB="13.0207", title="Title"):
    """

    :states: TODO
    :returns: TODO

    """
    energies    = "{"
    spins       = "{"
    occupations = "{"
    bands       = "{"

    for j,state in enumerate(states):
        if j == len(states)-1:
            separator="}"
        else:
            separator=", "
        energies+=str(state["energy"])+separator
        spins+=str(state["spin"])+separator
        occupations+=str(state["occupation"])+separator
        bands+=str(state["number"])+separator
    return """

string LUMO_TITLE="%s";

real ENERGIE_LB_PRISTINE   = %s ;
real ENERGIE_VB_PRISTINE   = %s ;

real OBERKANTE     = 100;
real UNTERKANTE    = 0;
real IMG_WIDTH     = 50;
real KANTEN_HEIGHT = 20;

real[] UNEXCITED_ENERGIES   = %s;
real[] UNEXCITED_SPINS      = %s;
real[] UNEXCITED_OCCUPATION = %s;
real[] UNEXCITED_BANDS      = %s;

//size(5cm,5cm);
unitsize(.2cm);
//unitsize(.1cm);


struct state {
  real energy;
  real occupation;
  real band;
  real value;
  string title           = "";
  real spin              = 0;
  real VB                = ENERGIE_VB_PRISTINE;
  real LB                = ENERGIE_LB_PRISTINE;
  real DASH_WIDTH        = 25;
  real DASH_HEIGHT       = 1.8;
  real X_COORD           = 0;
  real Y_OFFSET          = 0;
  real OCCUPATION_CUTOFF = 0.1;
  real getPlottingValue (){
    real val = 100*(energy - VB)/(LB-VB);
    return val + Y_OFFSET;
  };
  void init(real energy, real spin, real occupation, real band){
    this.energy     = energy;
    this.occupation = occupation;
    this.band       = band;
    this.spin       = spin;
    this.value      = getPlottingValue();
  };
  bool isOccupied(){
    if ( occupation >= OCCUPATION_CUTOFF ) {
      return true;
    } else {
      return false;
    }
  };
  pair getMiddlePoint (  ){
    real x,y;
    x = X_COORD+(DASH_WIDTH)/2;
    y = value + (DASH_HEIGHT)/2;
    return (x,y);
  };
  bool isUp (){   return spin == 1?true:false; };
  bool isDown (){ return spin == 2?true:false; };
  pair getSpinPosition (bool up=false){
    real x_deviation = 0.25*DASH_WIDTH;
    pair middle      = getMiddlePoint();
    if (up) {
      return (middle - (-x_deviation,0));
    } else {
      return (middle + (-x_deviation,0));
    }
  };
  path getSpinArrow (){
    bool up = isUp();
    pair position = getSpinPosition(up);
    real height = 3*DASH_HEIGHT;
    if (isUp()) {
      return position - (0,height/2) -- position + (0,height/2);
    } else {
      return position + (0,height/2) -- position - (0,height/2);
    }
  };
  void draw_spin(){
    pen style;
    real height          = 2*DASH_HEIGHT;
    pen unoccupied_style = 0.7*white+dashed;
    pen occupied_style   = black;
    if ( isOccupied() ) {
      style = occupied_style;
    } else {
      style = unoccupied_style;
    }
    path spinArrow = getSpinArrow();
    draw(spinArrow, linewidth(3)+style,Arrow(15));
  };
  void draw (
      bool draw_band       = false,
      bool draw_occupation = true
      ){
    pen style = red;
    real OCCUPATION_CUTOFF=0.1;
    if (occupation<=OCCUPATION_CUTOFF){
      style=gray;
    }
    filldraw(
        box(
          (X_COORD,value)
          ,(X_COORD+DASH_WIDTH,value+DASH_HEIGHT)
          ),
        style,style*.7
        );
    if ( draw_band )
      label(scale(1)*(string)band       , getMiddlePoint() - (DASH_WIDTH/4 , 0) , black);
    if ( draw_occupation && occupation != 0)
      label(scale(1)*(string)occupation , getSpinPosition(!isUp()) , black);
    if ( spin != 0 ) draw_spin();

  };
};



//----------------------------
//-  Valence and Cond bands  -
//----------------------------


label(LUMO_TITLE, (25, 100+KANTEN_HEIGHT/1.1), 0.8*blue);

path UNTERKANTE_BOX = box((0 , UNTERKANTE) , (IMG_WIDTH , UNTERKANTE - KANTEN_HEIGHT));
path OBERKANTE_BOX  = box((0 , OBERKANTE)  , (IMG_WIDTH , OBERKANTE + KANTEN_HEIGHT));

pen bandStyle = .8*white;
filldraw(OBERKANTE_BOX  , bandStyle, bandStyle);
filldraw(UNTERKANTE_BOX , bandStyle, bandStyle);







/***************/
/* DRAW STATES */
/***************/

for ( int i = 0; i < UNEXCITED_ENERGIES.length; i+=1 ) {
  int controller;
  if ( i%%2 == 0 ) {
    controller = 0;
  } else {
    controller = 1;
  }

  state s;

  s.init(
      UNEXCITED_ENERGIES[i],
      UNEXCITED_SPINS[i],
      UNEXCITED_OCCUPATION[i],
      UNEXCITED_BANDS[i]
  );

  s.X_COORD=0+controller*(s.DASH_WIDTH);
  if ( controller == 0 ) {
    label((string)s.energy, (s.X_COORD,s.value), W, red);
  } else {
    label((string)s.energy, (s.X_COORD+s.DASH_WIDTH, s.value), E, red);
  }
  s.draw();

}


//-----------
//-  SCALE  -
//-----------

real pointsToEnergy ( real point ){
  return (ENERGIE_LB_PRISTINE-ENERGIE_VB_PRISTINE)*point/100 + ENERGIE_VB_PRISTINE;
};
int steps = 5;
real width = 100/steps;

// Bandgap

draw((50,0)--(50,100),dashed+linewidth(.5), Bars(4mm));
label((string)(ENERGIE_LB_PRISTINE-ENERGIE_VB_PRISTINE)+" eV", (50,50), Fill(white));
label("VB", (IMG_WIDTH,0)+UNTERKANTE, N, Fill(white));
label("CB", (IMG_WIDTH,100)+UNTERKANTE, S, Fill(white));


// SCALE
draw((0,0)--(0,100), linewidth(1));
for ( int i = 0; i <= steps; i+=1 ) {
  // SCALE TICKS
  draw((0,width*i)--(2,width*i));
  // SCALE LABELS
  label(scale(0.7)*(string)pointsToEnergy(width*i), (1,width*i), E, Fill(white));
}

// vim: nospell
//vim-run: asy -f pdf %% && mupdf $(basename %% .asy).pdf &
//vim-run: asy -batchView



"""%(title, LB, VB, energies, spins, occupations, bands)

