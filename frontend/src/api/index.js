import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({ baseURL: API_BASE });

export const uploadPdf = (formData) => api.post('/ocr/upload-pdf', formData);
export const uploadBatch = (formData) => api.post('/ocr/batch-upload', formData);
export const getJobStatus = (jobId) => api.get(`/jobs/${jobId}`);
export const getJobHistory = (limit = 100) => api.get('/jobs/history', { params: { limit } });
export const getBookPages = async (bookName) => {
  const res = await api.get(`/books/${encodeURIComponent(bookName)}/pages`);
  return res.data;
};
export const getPageDetail = async (bookName, pageNumber) => {
  const res = await api.get(`/books/${encodeURIComponent(bookName)}/pages/${pageNumber}`);
  return res.data;
};
export const saveCorrectedTextApi = (bookName, pageNumber, text) =>
  api.put(`/books/${encodeURIComponent(bookName)}/pages/${pageNumber}/corrected-text`, { text });
export const downloadBookTxtApi = (bookName) =>
  api.get(`/books/${encodeURIComponent(bookName)}/export/txt`, {
    responseType: 'blob',
  });