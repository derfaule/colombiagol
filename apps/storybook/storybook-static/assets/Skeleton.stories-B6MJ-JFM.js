import{j as e}from"./jsx-runtime-D_zvdyIk.js";import{a as j}from"./utils-DclmTqRz.js";function s({className:c,...o}){return e.jsx("div",{"data-slot":"skeleton",className:j("animate-pulse rounded-md bg-muted",c),...o})}s.__docgenInfo={description:"",methods:[],displayName:"Skeleton"};const v={title:"UI/Skeleton",component:s,tags:["autodocs"]},a={render:()=>e.jsx(s,{className:"h-4 w-48"})},r={render:()=>e.jsxs("div",{className:"w-64 space-y-3 rounded-lg border p-4",children:[e.jsx(s,{className:"h-4 w-36"}),e.jsx(s,{className:"h-3 w-24"}),e.jsx(s,{className:"h-3 w-20"})]})},n={render:()=>e.jsxs("div",{className:"w-full space-y-2",children:[e.jsx(s,{className:"h-8 w-full"}),Array.from({length:5}).map((c,o)=>e.jsx(s,{className:"h-6 w-full"},o))]})},l={render:()=>e.jsxs("div",{className:"flex items-center gap-3 w-80",children:[e.jsx(s,{className:"h-3 w-20"}),e.jsx(s,{className:"h-5 w-6 rounded-full"}),e.jsx(s,{className:"h-3 flex-1"}),e.jsx(s,{className:"h-4 w-10"})]})};var t,m,d;a.parameters={...a.parameters,docs:{...(t=a.parameters)==null?void 0:t.docs,source:{originalSource:`{
  render: () => <Skeleton className="h-4 w-48" />
}`,...(d=(m=a.parameters)==null?void 0:m.docs)==null?void 0:d.source}}};var i,p,u;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  render: () => <div className="w-64 space-y-3 rounded-lg border p-4">
      <Skeleton className="h-4 w-36" />
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-3 w-20" />
    </div>
}`,...(u=(p=r.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var h,N,w;n.parameters={...n.parameters,docs:{...(h=n.parameters)==null?void 0:h.docs,source:{originalSource:`{
  render: () => <div className="w-full space-y-2">
      <Skeleton className="h-8 w-full" />
      {Array.from({
      length: 5
    }).map((_, i) => <Skeleton key={i} className="h-6 w-full" />)}
    </div>
}`,...(w=(N=n.parameters)==null?void 0:N.docs)==null?void 0:w.source}}};var x,f,S;l.parameters={...l.parameters,docs:{...(x=l.parameters)==null?void 0:x.docs,source:{originalSource:`{
  render: () => <div className="flex items-center gap-3 w-80">
      <Skeleton className="h-3 w-20" />
      <Skeleton className="h-5 w-6 rounded-full" />
      <Skeleton className="h-3 flex-1" />
      <Skeleton className="h-4 w-10" />
    </div>
}`,...(S=(f=l.parameters)==null?void 0:f.docs)==null?void 0:S.source}}};const y=["Default","SeasonCard","StandingsTable","MatchRow"];export{a as Default,l as MatchRow,r as SeasonCard,n as StandingsTable,y as __namedExportsOrder,v as default};
