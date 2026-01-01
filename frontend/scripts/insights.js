["Peak usage during evening hours",
 "AC is the highest energy consumer",
 "LED lighting can reduce usage by 10%"]
.forEach(t=>{
 let li=document.createElement("li");
 li.textContent="💡 "+t;
 document.getElementById("insights").appendChild(li);
});
