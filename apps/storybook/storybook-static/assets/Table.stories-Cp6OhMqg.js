import{j as e}from"./jsx-runtime-D_zvdyIk.js";import{T as o,b as x,e as g,f as n,d as l,a as h,c as s}from"./table-BUVh6Df6.js";import{B as p}from"./badge-C3yipnd7.js";import"./utils-DclmTqRz.js";import"./index-DQHfBcw3.js";import"./index-N1IydABH.js";import"./index-DzGJhHoF.js";const k={title:"UI/Table",component:o,tags:["autodocs"]},N=[{pos:1,team:"Atlético Nacional",p:38,w:24,d:8,l:6,gf:72,ga:32,pts:80},{pos:2,team:"Millonarios FC",p:38,w:21,d:9,l:8,gf:61,ga:38,pts:72},{pos:3,team:"Deportivo Cali",p:38,w:19,d:11,l:8,gf:58,ga:41,pts:68},{pos:4,team:"Independiente Medellín",p:38,w:18,d:10,l:10,gf:54,ga:44,pts:64},{pos:5,team:"Atlético Junior",p:38,w:17,d:12,l:9,gf:52,ga:42,pts:63}],t={render:()=>e.jsxs(o,{children:[e.jsx(x,{children:"Liga BetPlay 2023 Apertura — Final Standings"}),e.jsx(g,{children:e.jsxs(n,{children:[e.jsx(l,{className:"w-8",children:"#"}),e.jsx(l,{children:"Team"}),e.jsx(l,{className:"text-right",children:"P"}),e.jsx(l,{className:"text-right",children:"W"}),e.jsx(l,{className:"text-right",children:"D"}),e.jsx(l,{className:"text-right",children:"L"}),e.jsx(l,{className:"text-right",children:"GF"}),e.jsx(l,{className:"text-right",children:"GA"}),e.jsx(l,{className:"text-right",children:"Pts"})]})}),e.jsx(h,{children:N.map(a=>e.jsxs(n,{children:[e.jsx(s,{className:"font-mono text-muted-foreground",children:a.pos}),e.jsx(s,{className:"font-medium",children:a.team}),e.jsx(s,{className:"text-right",children:a.p}),e.jsx(s,{className:"text-right",children:a.w}),e.jsx(s,{className:"text-right",children:a.d}),e.jsx(s,{className:"text-right",children:a.l}),e.jsx(s,{className:"text-right",children:a.gf}),e.jsx(s,{className:"text-right",children:a.ga}),e.jsx(s,{className:"text-right font-bold",children:a.pts})]},a.pos))})]})},r={render:()=>e.jsxs(o,{children:[e.jsx(x,{children:"Top Scorers — 2023 Apertura"}),e.jsx(g,{children:e.jsxs(n,{children:[e.jsx(l,{children:"#"}),e.jsx(l,{children:"Player"}),e.jsx(l,{children:"Team"}),e.jsx(l,{className:"text-right",children:"Goals"}),e.jsx(l,{className:"text-right",children:"Pens"})]})}),e.jsx(h,{children:[{rank:1,player:"Jefferson Duque",team:"Nacional",goals:18,pens:3},{rank:2,player:"Dayro Moreno",team:"Once Caldas",goals:15,pens:2},{rank:3,player:"Leonardo Castro",team:"Millonarios",goals:13,pens:1}].map(a=>e.jsxs(n,{children:[e.jsx(s,{className:"text-muted-foreground",children:a.rank}),e.jsx(s,{className:"font-medium",children:a.player}),e.jsx(s,{children:e.jsx(p,{variant:"outline",children:a.team})}),e.jsx(s,{className:"text-right font-bold",children:a.goals}),e.jsx(s,{className:"text-right text-muted-foreground",children:a.pens})]},a.rank))})]})};var d,i,c;t.parameters={...t.parameters,docs:{...(d=t.parameters)==null?void 0:d.docs,source:{originalSource:`{
  render: () => <Table>
      <TableCaption>Liga BetPlay 2023 Apertura — Final Standings</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-8">#</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">P</TableHead>
          <TableHead className="text-right">W</TableHead>
          <TableHead className="text-right">D</TableHead>
          <TableHead className="text-right">L</TableHead>
          <TableHead className="text-right">GF</TableHead>
          <TableHead className="text-right">GA</TableHead>
          <TableHead className="text-right">Pts</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {standings.map(row => <TableRow key={row.pos}>
            <TableCell className="font-mono text-muted-foreground">{row.pos}</TableCell>
            <TableCell className="font-medium">{row.team}</TableCell>
            <TableCell className="text-right">{row.p}</TableCell>
            <TableCell className="text-right">{row.w}</TableCell>
            <TableCell className="text-right">{row.d}</TableCell>
            <TableCell className="text-right">{row.l}</TableCell>
            <TableCell className="text-right">{row.gf}</TableCell>
            <TableCell className="text-right">{row.ga}</TableCell>
            <TableCell className="text-right font-bold">{row.pts}</TableCell>
          </TableRow>)}
      </TableBody>
    </Table>
}`,...(c=(i=t.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var m,T,b;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: () => <Table>
      <TableCaption>Top Scorers — 2023 Apertura</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>#</TableHead>
          <TableHead>Player</TableHead>
          <TableHead>Team</TableHead>
          <TableHead className="text-right">Goals</TableHead>
          <TableHead className="text-right">Pens</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[{
        rank: 1,
        player: 'Jefferson Duque',
        team: 'Nacional',
        goals: 18,
        pens: 3
      }, {
        rank: 2,
        player: 'Dayro Moreno',
        team: 'Once Caldas',
        goals: 15,
        pens: 2
      }, {
        rank: 3,
        player: 'Leonardo Castro',
        team: 'Millonarios',
        goals: 13,
        pens: 1
      }].map(row => <TableRow key={row.rank}>
            <TableCell className="text-muted-foreground">{row.rank}</TableCell>
            <TableCell className="font-medium">{row.player}</TableCell>
            <TableCell>
              <Badge variant="outline">{row.team}</Badge>
            </TableCell>
            <TableCell className="text-right font-bold">{row.goals}</TableCell>
            <TableCell className="text-right text-muted-foreground">{row.pens}</TableCell>
          </TableRow>)}
      </TableBody>
    </Table>
}`,...(b=(T=r.parameters)==null?void 0:T.docs)==null?void 0:b.source}}};const B=["Standings","TopScorers"];export{t as Standings,r as TopScorers,B as __namedExportsOrder,k as default};
