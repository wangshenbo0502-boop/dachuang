import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";

const apiMock = vi.hoisted(() => ({ authMe: vi.fn(), getUser: vi.fn(), authLogout: vi.fn() }));
vi.mock("@/api", () => ({ api: apiMock }));

import { ApiError } from "@/api/request";
import { useAuthStore } from "./auth";
import { setAuthToken } from "@/utils/authSession";

beforeEach(() => {
  localStorage.clear();
  setAuthToken("valid-token");
  setActivePinia(createPinia());
  apiMock.authMe.mockReset();
  apiMock.getUser.mockReset();
});

describe("auth store fetchMe", () => {
  it("keeps the login when the network fails", async () => {
    apiMock.authMe.mockRejectedValue(new ApiError("服务连接失败，请确认后端已启动"));
    const store = useAuthStore();
    await expect(store.fetchMe()).rejects.toThrow();
    expect(store.token).toBe("valid-token");
    expect(localStorage.getItem("employment-platform-access-token")).toBe("valid-token");
  });

  it("keeps the login on server errors", async () => {
    apiMock.authMe.mockRejectedValue(new ApiError("服务器内部错误", 1, 500));
    const store = useAuthStore();
    await expect(store.fetchMe()).rejects.toThrow();
    expect(store.token).toBe("valid-token");
  });

  it("logs out when the token is rejected", async () => {
    apiMock.authMe.mockRejectedValue(new ApiError("登录凭证无效", 5102, 401));
    const store = useAuthStore();
    expect(await store.fetchMe()).toBeNull();
    expect(store.token).toBeNull();
    expect(localStorage.getItem("employment-platform-access-token")).toBeNull();
  });
});
