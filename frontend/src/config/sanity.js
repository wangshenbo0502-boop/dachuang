/**
 * Sanity CMS 已禁用 —— 大创项目使用 FastAPI 后端。
 * 保留此模块接口形状，使 useSanityData 走本地 fallback 数据。
 */

export const sanityClient = {
  config: () => ({ projectId: 'YOUR_PROJECT_ID' }),
  fetch: async () => [],
};

export const urlFor = () => ({
  width: () => ({
    quality: () => ({
      auto: () => ({
        url: () => '',
      }),
    }),
  }),
});

export const getProxyUrl = () => null;
