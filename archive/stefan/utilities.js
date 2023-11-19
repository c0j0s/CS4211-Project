(() => {
  const homeNameString =
    "Artur Boruc,Simon Francis,Tommy Elphick,Steve Cook,Charlie Daniels,Matt Ritchie,Dan Gosling,Andrew Surman,Marc Pugh,Joshua King,Callum Wilson";
  const homePositionString = "C,R,CR,CL,L,R,CR,CL,L,CR,CL";

  const homeNames = homeNameString.split(",");
  const homePositions = homePositionString.split(",");

  console.log("\n===== HOME =====");
  for (let i = 0; i < homeNames.length; i++) {
    const name = homeNames[i];
    const position = homePositions[i];
    console.log(`${name} is at position ${position}`);
  }

  // ==========================================================================

  const awayNameString =
    "Brad Guzan,Leandro Bacuna,Micah Richards,Ciaran Clark,Jordan Amavi,Jordan Veretout,Ashley Westwood,Idrissa Gueye,Jordan Ayew,Gabriel Agbonlahor,Scott Sinclair";
  const awayPositionString = "C,R,CR,CL,L,RL,C,LR,RL,C,LR";

  const awayNames = awayNameString.split(",");
  const awayPositions = awayPositionString.split(",");

  console.log("\n===== AWAY =====");
  for (let i = 0; i < awayNames.length; i++) {
    const name = awayNames[i];
    const position = awayPositions[i];
    console.log(`${name} is at position ${position}`);
  }

  console.log("");
})();

/*

===== HOME =====
Artur Boruc is at position C
Simon Francis is at position R
Tommy Elphick is at position CR
Steve Cook is at position CL
Charlie Daniels is at position L
Matt Ritchie is at position R
Dan Gosling is at position CR
Andrew Surman is at position CL
Marc Pugh is at position L
Joshua King is at position CR
Callum Wilson is at position CL

===== AWAY =====
Brad Guzan is at position C
Leandro Bacuna is at position R
Micah Richards is at position CR
Ciaran Clark is at position CL
Jordan Amavi is at position L
Jordan Veretout is at position RL
Ashley Westwood is at position C
Idrissa Gueye is at position LR
Jordan Ayew is at position RL
Gabriel Agbonlahor is at position C
Scott Sinclair is at position LR

*/
