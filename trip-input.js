(function(root){
  "use strict";
  const aliases={
    service_type:["서비스구분","서비스 구분","구분","service_type","type"],
    trip_date:["운행일","날짜","trip_date"],
    departure_time:["출발시간","출발 시간","시간","departure_time"],
    origin:["출발지","origin"],destination:["도착지","destination"],fare_krw:["금액","요금","fare_krw"]
  };
  const privateRoute=/(?<!\d)01[016789][ -]?\d{3,4}[ -]?\d{4}(?!\d)|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\d{6}\s*[-]\s*[1-4]\d{6}|카드번호|콜센터|고객명|담당자|연락처|(?:^|\s)[가-힣]{2,4}\s*\)/i;
  function validateTrip(trip){
    if(!["daeri","transport"].includes(trip.service_type))throw new Error("서비스 구분을 확인하세요.");
    if(!/^\d{4}-\d{2}-\d{2}$/.test(trip.trip_date))throw new Error("운행일은 YYYY-MM-DD 형식이어야 합니다.");
    const date=new Date(trip.trip_date+"T00:00:00Z");
    if(!Number.isFinite(date.getTime())||date.toISOString().slice(0,10)!==trip.trip_date)throw new Error("실제로 존재하는 운행일을 입력하세요.");
    if(!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(trip.departure_time))throw new Error("출발 시간은 HH:MM 형식이어야 합니다.");
    for(const key of ["origin","destination"]){
      const value=trip[key];
      if(typeof value!=="string"||!value.trim()||value.length>200||/[\r\n]/.test(value))throw new Error("출발지·도착지는 한 줄로 200자 이내로 입력하세요.");
      if(privateRoute.test(value))throw new Error("장소명에서 개인정보 또는 업무 메모를 제거한 뒤 다시 확인하세요.");
    }
    if(!Number.isInteger(trip.fare_krw)||trip.fare_krw<=0||trip.fare_krw>2147483647)throw new Error("금액은 올바른 원 단위 양의 정수여야 합니다.");
    if(!["completed","pending","cancelled"].includes(trip.status))throw new Error("운행 상태를 확인하세요.");
    return trip;
  }
  function parseCSV(raw){
    const rows=[];let row=[],value="",quoted=false,closed=false;
    const text=String(raw).replace(/^\uFEFF/,"");
    function cell(){row.push(value.trim());value="";closed=false;}
    function line(){cell();if(row.some(Boolean))rows.push(row);row=[];}
    for(let i=0;i<text.length;i++){
      const ch=text[i];
      if(quoted){if(ch==='"'){if(text[i+1]==='"'){value+='"';i++;}else{quoted=false;closed=true;}}else value+=ch;continue;}
      if(ch===","){cell();continue;}
      if(ch==="\n"||ch==="\r"){if(ch==="\r"&&text[i+1]==="\n")i++;line();continue;}
      if(ch==='"'){if(value.trim()||closed)throw new Error("CSV 따옴표 위치를 확인하세요.");value="";quoted=true;continue;}
      if(closed){if(!/\s/.test(ch))throw new Error("CSV 닫는 따옴표 뒤에는 쉼표가 필요합니다.");continue;}
      value+=ch;
    }
    if(quoted)throw new Error("CSV 따옴표가 닫히지 않았습니다.");
    if(value||row.length||closed)line();
    return rows;
  }
  function parseImport(raw){
    const table=parseCSV(raw);
    if(table.length<2)throw new Error("제목 행과 데이터 행이 필요합니다.");
    const header=table.shift().map(x=>x.toLowerCase());
    const columns=header.map(h=>Object.keys(aliases).find(key=>aliases[key].includes(h)));
    if(columns.some(x=>!x)||new Set(columns).size!==6||columns.length!==6)throw new Error("서비스구분, 운행일, 출발시간, 출발지, 도착지, 금액의 6개 열만 사용하세요. 개인정보 열은 제외하세요.");
    return table.map((cells,index)=>{
      try{
        if(cells.length!==6)throw new Error("열 수가 맞지 않습니다. 빠진 값이나 쉼표·따옴표를 확인하세요.");
        const trip=Object.fromEntries(columns.map((key,i)=>[key,cells[i]]));
        const kind=trip.service_type.toLowerCase();
        trip.service_type=kind==="탁송"||kind==="transport"?"transport":kind==="대리운전"||kind==="daeri"?"daeri":"";
        trip.fare_krw=Number(trip.fare_krw.replace(/[₩원,\s]/g,""));trip.status="completed";
        return validateTrip(trip);
      }catch(error){throw new Error((index+2)+"번째 데이터 행: "+error.message);}
    });
  }
  const api={validateTrip,parseCSV,parseImport};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  else root.SmartBunnyTripInput=api;
})(typeof window!=="undefined"?window:globalThis);
