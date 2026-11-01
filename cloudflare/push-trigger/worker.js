// GitHub 的定时任务被限流到每天 4-6 次，常常跳过推送时段，所以由这里准点触发工作流。
const DISPATCH_URL =
  "https://api.github.com/repos/zhuofanl770-dotcom/TrendRadar/actions/workflows/crawler.yml/dispatches";

export default {
  async scheduled(_event, env) {
    const response = await fetch(DISPATCH_URL, {
      method: "POST",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        "User-Agent": "trendradar-push-trigger",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      body: JSON.stringify({ ref: "master" }),
    });
    if (response.ok) return;

    // token 过期这类失败没有其他地方能看到，直接推到手机上
    const detail = `GitHub 返回 ${response.status}：${await response.text()}`;
    await fetch(`https://ntfy.sh/${env.NTFY_TOPIC}`, {
      method: "POST",
      headers: { Title: "TrendRadar trigger failed" },
      body: detail,
    });
    throw new Error(detail);
  },
};
