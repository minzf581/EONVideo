import { Composition } from "remotion";

import { FinanceAdvisoryVideo, financeVideoSchema } from "./templates/FinanceAdvisoryVideo";

export function RemotionRoot() {
  return (
    <Composition
      component={FinanceAdvisoryVideo}
      defaultProps={{
        title: "新加坡融资窗口来了？",
        subtitle: "中国企业出海融资，真正要准备的是资本结构",
        bullets: ["市场窗口", "融资路径", "资本结构", "风险提示"],
        riskNotice: "内容仅作市场观察，不构成投资、法律或税务建议。",
      }}
      durationInFrames={1800}
      fps={30}
      height={1920}
      id="FinanceAdvisoryVideo"
      schema={financeVideoSchema}
      width={1080}
    />
  );
}

