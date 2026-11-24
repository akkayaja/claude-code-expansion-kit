// 서비스 워커 = 앱 파일을 휴대폰 안에 보관해 두는 '보관 담당'.
// 처음 열 때 아래 파일들을 보관함(캐시)에 넣어 두고,
// 다음부터는 인터넷보다 보관함을 먼저 봐서 비행기 모드에서도 열려요.
// 앱을 고치면 VERSION 숫자를 올려야 휴대폰이 새 파일로 바꿔요.
const VERSION = 'water-v2';
const FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

// 설치될 때: 파일들을 보관함에 담기
self.addEventListener('install', event => {
  event.waitUntil(caches.open(VERSION).then(cache => cache.addAll(FILES)));
  self.skipWaiting();
});

// 새 버전이 켜질 때: 옛날 보관함 지우기
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

// 파일을 달라고 할 때: 보관함에 있으면 그걸 주고, 없으면 인터넷에서 가져오기
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request, { ignoreSearch: true }).then(hit => hit || fetch(event.request))
  );
});
