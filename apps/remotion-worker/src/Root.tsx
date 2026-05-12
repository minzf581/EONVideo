import React from "react";
import { Composition } from "remotion";

import { CapitalNews, capitalNewsSchema } from "./templates/CapitalNews.js";

export function RemotionRoot() {
  return (
    <Composition
      component={CapitalNews}
      defaultProps={{
        title: "新加坡资本市场新信号",
        subtitle: "企业出海融资，需要重新审视资本结构",
        script: "这是一条财经短视频脚本。重点不是追热点，而是理解热点对融资、上市路径和海外投资人沟通的影响。",
        bullets: ["海外融资", "资本结构", "投资人沟通"],
        brandName: "EONVideo Capital Brief",
        cta: "关注我，了解更多海外融资和新加坡资本市场观察。",
      }}
      durationInFrames={1800}
      fps={30}
      height={1920}
      id="CapitalNews"
      schema={capitalNewsSchema}
      width={1080}
    />
  );
}

