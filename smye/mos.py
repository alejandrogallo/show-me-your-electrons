
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

real[] UNEXCITED_ENERGIES=%s;
real[] UNEXCITED_SPINS=%s;
real[] UNEXCITED_OCCUPATION=%s;
real[] UNEXCITED_BANDS=%s;

//size(5cm,5cm);
unitsize(.2cm);


struct state {
  real energy;
  real occupation;
  real band;
  real value;
  string title     = "";
  real spin        = 0;
  real VB          = ENERGIE_VB_PRISTINE;
  real LB          = ENERGIE_LB_PRISTINE;
  real DASH_WIDTH  = 25;
  real DASH_HEIGHT = 1;
  real X_COORD     = 0;
  real Y_OFFSET    = 0;
  real getPlottingValue ( ){
    real val = 100*(energy - VB)/(LB-VB);
    return val + Y_OFFSET;
  };
  void init(real e, real s, real o, real b){
    energy     = e;
    if ( o<0.5 ) {
      occupation = 0;
    } else {
      occupation = 1;
    }
    band       = b;
    spin       = s;
    value      = getPlottingValue();
  };
  pair getMiddlePoint (  ){
    real x,y;
    x = X_COORD+(DASH_WIDTH)/2;
    y = value + (DASH_HEIGHT)/2;
    return (x,y);
  };
  void draw_spin(){
    pair middle = getMiddlePoint();
    path ar;
    real x_deviation = 0.25*DASH_WIDTH;
    real height = 5*DASH_HEIGHT;
    pen unoccupied_style = 0.7*white+dashed, occupied_style = black, style;
    if ( occupation == 1 ) {
      style = occupied_style;
    } else {
      style = unoccupied_style;
    }
    if ( spin == 1 ) {
      ar = (middle - (-x_deviation,height))..(middle + (x_deviation,height));
    } else {
      ar = (middle + (-x_deviation,height))..(middle - (x_deviation,height));
    }
    draw(ar, linewidth(1)+style,Arrow());
  };
  void draw (){
    pen style = red;
    //label((string)energy, (X_COORD+DASH_WIDTH,value), E);
    if ( spin != 0 ) {
      draw_spin();
    } else{
      if (occupation==0){
        style=blue;
      }
    }
    filldraw(box((X_COORD,value),(X_COORD+DASH_WIDTH,value+DASH_HEIGHT)),style);
  };
};


/*******************/
/* DRAW DECORATION */
/*******************/
real pointsToEnergy ( real point ){
  return (ENERGIE_LB_PRISTINE-ENERGIE_VB_PRISTINE)*point/100 + ENERGIE_VB_PRISTINE;
};
label(LUMO_TITLE, (25, 100+KANTEN_HEIGHT/1.1), 0.8*blue);
draw((50,0)--(50,100),dashed, Arrows);
label((string)(ENERGIE_LB_PRISTINE-ENERGIE_VB_PRISTINE)+" eV", (50,50), Fill(white));

label("Leitungsband" , (IMG_WIDTH/2 , OBERKANTE+(KANTEN_HEIGHT)/2));
label("Valenzband"   , (IMG_WIDTH/2 , (UNTERKANTE-KANTEN_HEIGHT)/2));

path UNTERKANTE_BOX = box((0 , UNTERKANTE) , (IMG_WIDTH , UNTERKANTE - KANTEN_HEIGHT));
path OBERKANTE_BOX  = box((0 , OBERKANTE)  , (IMG_WIDTH , OBERKANTE + KANTEN_HEIGHT));

filldraw(OBERKANTE_BOX  , .8*white);
filldraw(UNTERKANTE_BOX , .8*white);



int steps = 5;
real width = 100/5;
draw((0,0)--(0,100), linewidth(1));
for ( int i = 0; i <= steps; i+=1 ) {
  draw((0,width*i)--(2,width*i));
  label(scale(0.7)*(string)pointsToEnergy(width*i), (1,width*i), E, Fill(white));
}




/***************/
/* DRAW STATES */
/***************/

for ( int i = 0; i < UNEXCITED_ENERGIES.length; i+=1 ) {
  int controller;
  if ( i%s2 == 0 ) {
    controller = 0;
  } else {
    controller = 1;
  }
  state s;
  s.init(UNEXCITED_ENERGIES[i], UNEXCITED_SPINS[i], UNEXCITED_OCCUPATION[i], UNEXCITED_BANDS[i]);
  s.X_COORD=0+controller*(s.DASH_WIDTH);
  if ( controller == 0 ) {
    label((string)s.energy, (s.X_COORD,s.value), W, 0.5*white);
  } else {
    label((string)s.energy, (s.X_COORD+s.DASH_WIDTH,s.value), E, 0.5*white);
  }
  label(scale(.5)*(string)s.band, s.getMiddlePoint(), 0.7*white);
  s.draw();

}
"""%(title, LB, VB, energies, spins, occupations, bands, "%")

