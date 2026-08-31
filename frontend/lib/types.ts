export type QueryRequest = {
  query: string;
  document_id?: string;
};

export type QueryResponse = {
  answer: string;
};

export type UploadResponse = {
  document_id: string;
  filename: string;
  chunk_count: number;
};
