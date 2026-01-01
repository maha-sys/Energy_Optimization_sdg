new Chart(document.getElementById("energyChart"),{
 type:"line",
 data:{
  labels:["Jan","Feb","Mar","Apr","May","Jun"],
  datasets:[{
   label:"Energy Usage (kWh)",
   data:[320,340,360,380,400,420],
   borderColor:"#38bdf8",
   backgroundColor:"rgba(56,189,248,0.2)",
   tension:0.45,
   fill:true
  }]
 },
 options:{
  plugins:{ legend:{ labels:{ color:"#e5e7eb" } } },
  scales:{
   x:{ ticks:{ color:"#9ca3af" } },
   y:{ ticks:{ color:"#9ca3af" } }
  }
 }
});
