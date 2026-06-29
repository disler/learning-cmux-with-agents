// Tiny typed client over the Flotion REST API. The dev server proxies /api to
// the FastAPI backend (see vite.config.ts), so paths are origin-relative.

export interface Page {
  id: number;
  title: string;
  parent_id: number | null;
  position: number;
}

export interface Block {
  id: number;
  page_id: number;
  type: string;
  content: string;
  position: number;
}

export interface PageDetail extends Page {
  blocks: Block[];
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} → ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listPages: () => req<Page[]>("/pages"),
  createPage: (title = "Untitled") =>
    req<Page>("/pages", { method: "POST", body: JSON.stringify({ title }) }),
  getPage: (id: number) => req<PageDetail>(`/pages/${id}`),
  updatePage: (id: number, patch: Partial<Pick<Page, "title" | "position">>) =>
    req<Page>(`/pages/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deletePage: (id: number) => req<void>(`/pages/${id}`, { method: "DELETE" }),

  createBlock: (
    pageId: number,
    block: { type?: string; content?: string; position?: number },
  ) =>
    req<Block>(`/pages/${pageId}/blocks`, {
      method: "POST",
      body: JSON.stringify(block),
    }),
  updateBlock: (
    id: number,
    patch: Partial<Pick<Block, "type" | "content" | "position">>,
  ) =>
    req<Block>(`/blocks/${id}`, { method: "PATCH", body: JSON.stringify(patch) }),
  deleteBlock: (id: number) => req<void>(`/blocks/${id}`, { method: "DELETE" }),
};
