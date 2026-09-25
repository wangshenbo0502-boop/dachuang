export const fmt=(v?:string|null)=>v?new Intl.DateTimeFormat("zh-CN",{dateStyle:"medium",timeStyle:"short"}).format(new Date(v)):"--";
export const err=(e:unknown)=>e instanceof Error?e.message:"操作失败，请稍后重试";
export const text=(v="")=>v.replace(/```[\s\S]*?```/g,"").replace(/[#>*_`\[\]|-]/g," ").replace(/\s+/g," ").trim();
