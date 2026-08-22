import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getProducts = async (params = {}) => {
  const response = await api.get("/products", { params });
  return Array.isArray(response.data) ? response.data : (response.data.products || []);
};

export const getProductDetails = async (variantId) => {
  const response = await api.get(`/products/${variantId}`);
  return response.data;
};

export const getPriceAnalytics = async (variantId) => {
  const response = await api.get(`/analytics/price/${variantId}`);
  return response.data;
};

export const getPriceHistory = async (variantId) => {
  const response = await api.get(`/analytics/history/${variantId}`);
  return response.data;
};

export const getAspectSentiment = async (variantId) => {
  const response = await api.get(`/reviews/aspects/${variantId}`);
  return response.data;
};

export const askReviewQA = async (variantId, question) => {
  const response = await api.post("/reviews/qa", {
    variant_id: variantId,
    question,
  });
  return response.data;
};

export const getSampleReviews = async (variantId, limit = 8) => {
  const response = await api.get(`/reviews/${variantId}`, { params: { limit } });
  return response.data;
};

export const searchRecommendations = async (payload) => {
  const response = await api.post("/recommendations/search", payload);
  return response.data;
};

export const parseQuery = async (query) => {
  const response = await api.post("/recommendations/parse-query", { query });
  return response.data;
};

export default api;
