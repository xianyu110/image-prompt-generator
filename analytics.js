const GA_MEASUREMENT_ID = "G-8QJK65VQ73";
const ANALYTICS_HOSTS = new Set([
  "image-prompt-generator.com",
  "www.image-prompt-generator.com",
]);

function isValidMeasurementId(measurementId) {
  return /^G-[A-Z0-9]+$/.test(measurementId) && measurementId !== "G-XXXXXXXXXX";
}

function initGoogleAnalytics() {
  if (!ANALYTICS_HOSTS.has(window.location.hostname)) return;
  if (!isValidMeasurementId(GA_MEASUREMENT_ID)) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };

  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(GA_MEASUREMENT_ID)}`;
  document.head.appendChild(script);

  window.gtag("js", new Date());
  window.gtag("config", GA_MEASUREMENT_ID);
}

initGoogleAnalytics();
