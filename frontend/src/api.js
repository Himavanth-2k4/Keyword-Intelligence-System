import axios from 'axios';


const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';


export const postExtract = (payload) => axios.post(`${API_BASE}/extract`, payload).then(r=>r.data);
export const postExtractPDF = (formData) => axios.post(`${API_BASE}/extract_pdf`, formData, {headers: {'Content-Type':'multipart/form-data'}}).then(r=>r.data);