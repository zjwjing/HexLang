// YuanHui Nested Counter — 邵雍《皇极经世》元会运世嵌套计数器
// 定位：四层嵌套模运算原型，与计算机年-月-日-时分秒嵌套计数器同构
// 工程化映射规则（非历史纪年）：
//   1元 = 12会 → mod12
//   1会 = 30运 → mod30
//   1运 = 12世 → mod12
//   1世 = 30年 → mod30
//   总周期：12×30×12×30 = 129600 单位

export class YuanHuiEncoder {
  encode(timestamp) {
    if (timestamp === undefined) timestamp = Math.floor(Date.now() / 1000);
    const t = Math.floor(timestamp);

    // 工程化映射：以秒为单位
    const YUAN_SEC = 12 * 30 * 12 * 30 * 24 * 3600; // 1元秒数
    const HUI_SEC = 30 * 12 * 30 * 24 * 3600;        // 1会秒数
    const YUN_SEC = 12 * 30 * 24 * 3600;              // 1运秒数
    const SHI_SEC = 30 * 24 * 3600;                   // 1世秒数

    const yuan = Math.floor(t / YUAN_SEC) % 12;
    const hui = Math.floor(t / HUI_SEC) % 30;
    const yun = Math.floor(t / YUN_SEC) % 12;
    const shi = Math.floor(t / SHI_SEC) % 30;

    const vector = [yuan / 12, hui / 30, yun / 12, shi / 30];

    return {
      timestamp: t,
      mode: 'yuanhui',
      yuan,
      hui,
      yun,
      shi,
      vector,
      note: '四层嵌套模运算原型，源自邵雍《皇极经世》元会运世',
    };
  }
}
