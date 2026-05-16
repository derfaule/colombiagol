import{j as a}from"./jsx-runtime-D_zvdyIk.js";import{a as j}from"./utils-DclmTqRz.js";import{r as S}from"./index-DzGJhHoF.js";import{P as g}from"./index-DGGqAipM.js";import"./index-Aa7ha4a9.js";import"./index-CzJRPfmc.js";import"./index-N1IydABH.js";var z="Separator",c="horizontal",A=["horizontal","vertical"],N=S.forwardRef((e,n)=>{const{decorative:i,orientation:r=c,...f}=e,l=O(r)?r:c,h=i?{role:"none"}:{"aria-orientation":l==="vertical"?l:void 0,role:"separator"};return a.jsx(g.div,{"data-orientation":l,...h,...f,ref:n})});N.displayName=z;function O(e){return A.includes(e)}var E=N;function t({className:e,orientation:n="horizontal",decorative:i=!0,...r}){return a.jsx(E,{"data-slot":"separator",decorative:i,orientation:n,className:j("shrink-0 bg-border data-horizontal:h-px data-horizontal:w-full data-vertical:w-px data-vertical:self-stretch",e),...r})}t.__docgenInfo={description:"",methods:[],displayName:"Separator",props:{orientation:{defaultValue:{value:'"horizontal"',computed:!1},required:!1},decorative:{defaultValue:{value:"true",computed:!1},required:!1}}};const F={title:"UI/Separator",component:t,tags:["autodocs"],argTypes:{orientation:{control:"select",options:["horizontal","vertical"]}}},s={render:()=>a.jsxs("div",{className:"w-64",children:[a.jsx("p",{className:"text-sm",children:"Atlético Nacional"}),a.jsx(t,{className:"my-3"}),a.jsx("p",{className:"text-sm text-muted-foreground",children:"18 titles"})]})},o={render:()=>a.jsxs("div",{className:"flex h-8 items-center gap-3",children:[a.jsx("span",{className:"text-sm",children:"Apertura"}),a.jsx(t,{orientation:"vertical"}),a.jsx("span",{className:"text-sm",children:"Clausura"}),a.jsx(t,{orientation:"vertical"}),a.jsx("span",{className:"text-sm",children:"Finals"})]})};var m,p,d;s.parameters={...s.parameters,docs:{...(m=s.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: () => <div className="w-64">
      <p className="text-sm">Atlético Nacional</p>
      <Separator className="my-3" />
      <p className="text-sm text-muted-foreground">18 titles</p>
    </div>
}`,...(d=(p=s.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};var u,x,v;o.parameters={...o.parameters,docs:{...(u=o.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: () => <div className="flex h-8 items-center gap-3">
      <span className="text-sm">Apertura</span>
      <Separator orientation="vertical" />
      <span className="text-sm">Clausura</span>
      <Separator orientation="vertical" />
      <span className="text-sm">Finals</span>
    </div>
}`,...(v=(x=o.parameters)==null?void 0:x.docs)==null?void 0:v.source}}};const b=["Horizontal","Vertical"];export{s as Horizontal,o as Vertical,b as __namedExportsOrder,F as default};
