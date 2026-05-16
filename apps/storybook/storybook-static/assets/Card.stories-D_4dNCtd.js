import{j as e}from"./jsx-runtime-D_zvdyIk.js";import{a as s}from"./utils-DclmTqRz.js";import{B as S}from"./badge-C3yipnd7.js";import{B as I}from"./button-BvwDOwPB.js";import"./index-DQHfBcw3.js";import"./index-N1IydABH.js";import"./index-DzGJhHoF.js";function t({className:a,size:r="default",...H}){return e.jsx("div",{"data-slot":"card","data-size":r,className:s("group/card flex flex-col gap-4 overflow-hidden rounded-lg bg-card py-4 text-xs/relaxed text-card-foreground ring-1 ring-foreground/10 has-[>img:first-child]:pt-0 data-[size=sm]:gap-3 data-[size=sm]:py-3 *:[img:first-child]:rounded-t-lg *:[img:last-child]:rounded-b-lg",a),...H})}function n({className:a,...r}){return e.jsx("div",{"data-slot":"card-header",className:s("group/card-header @container/card-header grid auto-rows-min items-start gap-1 rounded-t-lg px-4 group-data-[size=sm]/card:px-3 has-data-[slot=card-action]:grid-cols-[1fr_auto] has-data-[slot=card-description]:grid-rows-[auto_auto] [.border-b]:pb-4 group-data-[size=sm]/card:[.border-b]:pb-3",a),...r})}function o({className:a,...r}){return e.jsx("div",{"data-slot":"card-title",className:s("font-heading text-sm font-medium",a),...r})}function i({className:a,...r}){return e.jsx("div",{"data-slot":"card-description",className:s("text-xs/relaxed text-muted-foreground",a),...r})}function D({className:a,...r}){return e.jsx("div",{"data-slot":"card-action",className:s("col-start-2 row-span-2 row-start-1 self-start justify-self-end",a),...r})}function d({className:a,...r}){return e.jsx("div",{"data-slot":"card-content",className:s("px-4 group-data-[size=sm]/card:px-3",a),...r})}function T({className:a,...r}){return e.jsx("div",{"data-slot":"card-footer",className:s("flex items-center rounded-b-lg px-4 group-data-[size=sm]/card:px-3 [.border-t]:pt-4 group-data-[size=sm]/card:[.border-t]:pt-3",a),...r})}t.__docgenInfo={description:"",methods:[],displayName:"Card",props:{size:{required:!1,tsType:{name:"union",raw:'"default" | "sm"',elements:[{name:"literal",value:'"default"'},{name:"literal",value:'"sm"'}]},description:"",defaultValue:{value:'"default"',computed:!1}}}};n.__docgenInfo={description:"",methods:[],displayName:"CardHeader"};T.__docgenInfo={description:"",methods:[],displayName:"CardFooter"};o.__docgenInfo={description:"",methods:[],displayName:"CardTitle"};D.__docgenInfo={description:"",methods:[],displayName:"CardAction"};i.__docgenInfo={description:"",methods:[],displayName:"CardDescription"};d.__docgenInfo={description:"",methods:[],displayName:"CardContent"};const E={title:"UI/Card",component:t,tags:["autodocs"],argTypes:{size:{control:"select",options:["default","sm"]}}},c={render:()=>e.jsxs(t,{className:"w-72",children:[e.jsxs(n,{children:[e.jsx(o,{children:"Liga BetPlay 2023"}),e.jsx(i,{children:"Clausura · 20 teams"})]}),e.jsx(d,{children:e.jsx("p",{className:"text-muted-foreground",children:"380 matches played"})})]})},l={render:()=>e.jsxs(t,{className:"w-72",children:[e.jsxs(n,{children:[e.jsx(o,{children:"Atlético Nacional"}),e.jsx(D,{children:e.jsx(S,{variant:"secondary",children:"1st"})}),e.jsx(i,{children:"Liga BetPlay 2023 Apertura"})]}),e.jsx(d,{children:e.jsx("p",{children:"38 played · 24W 8D 6L"})}),e.jsx(T,{children:e.jsx(I,{size:"sm",variant:"outline",children:"View squad"})})]})},m={render:()=>e.jsxs(t,{size:"sm",className:"w-64",children:[e.jsxs(n,{children:[e.jsx(o,{children:"Millonarios FC"}),e.jsx(i,{children:"2022 Clausura"})]}),e.jsx(d,{children:e.jsx("p",{children:"Champion"})})]})},p={render:()=>e.jsx(t,{className:"w-80",children:e.jsxs(d,{className:"flex items-center justify-between py-4",children:[e.jsx("span",{className:"font-medium",children:"Millonarios"}),e.jsx("span",{className:"font-mono font-bold text-sm",children:"2 – 1"}),e.jsx("span",{className:"font-medium",children:"América"})]})})},u={render:()=>e.jsx("div",{className:"grid grid-cols-2 gap-3 w-[500px]",children:["2023 Apertura","2023 Clausura","2022 Apertura","2022 Clausura"].map(a=>e.jsxs(t,{size:"sm",children:[e.jsxs(n,{children:[e.jsx(o,{children:a}),e.jsx(i,{children:"Liga BetPlay"})]}),e.jsx(d,{children:e.jsx("p",{className:"text-muted-foreground",children:"180 matches"})})]},a))})};var C,x,h;c.parameters={...c.parameters,docs:{...(C=c.parameters)==null?void 0:C.docs,source:{originalSource:`{
  render: () => <Card className="w-72">
      <CardHeader>
        <CardTitle>Liga BetPlay 2023</CardTitle>
        <CardDescription>Clausura · 20 teams</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">380 matches played</p>
      </CardContent>
    </Card>
}`,...(h=(x=c.parameters)==null?void 0:x.docs)==null?void 0:h.source}}};var f,g,j;l.parameters={...l.parameters,docs:{...(f=l.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: () => <Card className="w-72">
      <CardHeader>
        <CardTitle>Atlético Nacional</CardTitle>
        <CardAction>
          <Badge variant="secondary">1st</Badge>
        </CardAction>
        <CardDescription>Liga BetPlay 2023 Apertura</CardDescription>
      </CardHeader>
      <CardContent>
        <p>38 played · 24W 8D 6L</p>
      </CardContent>
      <CardFooter>
        <Button size="sm" variant="outline">View squad</Button>
      </CardFooter>
    </Card>
}`,...(j=(g=l.parameters)==null?void 0:g.docs)==null?void 0:j.source}}};var N,y,w;m.parameters={...m.parameters,docs:{...(N=m.parameters)==null?void 0:N.docs,source:{originalSource:`{
  render: () => <Card size="sm" className="w-64">
      <CardHeader>
        <CardTitle>Millonarios FC</CardTitle>
        <CardDescription>2022 Clausura</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Champion</p>
      </CardContent>
    </Card>
}`,...(w=(y=m.parameters)==null?void 0:y.docs)==null?void 0:w.source}}};var v,_,b;p.parameters={...p.parameters,docs:{...(v=p.parameters)==null?void 0:v.docs,source:{originalSource:`{
  render: () => <Card className="w-80">
      <CardContent className="flex items-center justify-between py-4">
        <span className="font-medium">Millonarios</span>
        <span className="font-mono font-bold text-sm">2 – 1</span>
        <span className="font-medium">América</span>
      </CardContent>
    </Card>
}`,...(b=(_=p.parameters)==null?void 0:_.docs)==null?void 0:b.source}}};var z,A,B;u.parameters={...u.parameters,docs:{...(z=u.parameters)==null?void 0:z.docs,source:{originalSource:`{
  render: () => <div className="grid grid-cols-2 gap-3 w-[500px]">
      {['2023 Apertura', '2023 Clausura', '2022 Apertura', '2022 Clausura'].map(label => <Card key={label} size="sm">
          <CardHeader>
            <CardTitle>{label}</CardTitle>
            <CardDescription>Liga BetPlay</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">180 matches</p>
          </CardContent>
        </Card>)}
    </div>
}`,...(B=(A=u.parameters)==null?void 0:A.docs)==null?void 0:B.source}}};const G=["Default","WithAction","Small","MatchCard","SeasonGrid"];export{c as Default,p as MatchCard,u as SeasonGrid,m as Small,l as WithAction,G as __namedExportsOrder,E as default};
