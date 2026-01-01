function downloadCSV(){
 const csv="Metric,Value\nUsage,450 kWh\nSavings,15%";
 const blob=new Blob([csv],{type:"text/csv"});
 const a=document.createElement("a");
 a.href=URL.createObjectURL(blob);
 a.download="energy_report.csv";
 a.click();
}
