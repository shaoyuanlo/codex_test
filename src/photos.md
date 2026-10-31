---
layout: layouts/page.njk
section: photos
permalink: /photos/index.html
title: Photos
albums:
  - title: "Lab Promotional Video"
    photos:
      - src: /files/lab_photos/Trai_lab3.mp4
        type: video
        poster: /files/lab_photos/Trai_lab3-poster.jpg
        alt: Lab video
        caption: Lab Promotional Video (實驗室形象影片) @ Trai Lab (Oct 17, 2025)
  - title: "2026"
    photos:
      - src: /files/lab_photos/image_2F33A832.jpeg
        alt: Lab photo 1
        caption: Our First Lab Dinner (兆元宴) @ 磚窯古早味懷舊餐廳 (Mar 18, 2026)
      - src: /files/lab_photos/IMG_6450.jpg
        alt: Lab photo 2
        caption: ICML 2026 @ Seoul, South Korea (Jul 10, 2026)
      - src: /files/lab_photos/PXL_20260710_095915324.jpg
        alt: Lab photo 3
        caption: ICML 2026 @ Seoul, South Korea (Jul 10, 2026)
      - src: /files/lab_photos/PXL_20260710_103414851.jpg
        alt: Lab photo 4
        caption: ICML 2026 @ Seoul, South Korea (Jul 10, 2026)
      - src: /files/lab_photos/PXL_20260715_124218569.jpg
        alt: Lab photo 5
        caption: Rishabh Sain's Farewell (Jul 15, 2026)
      - src: /files/lab_photos/image_71B54162.jpeg
        alt: Lab photo 6
        caption: ICML 2026 @ Seoul, South Korea (Jul 09, 2026)    
      - src: /files/lab_photos/image_72910324.jpg
        alt: Lab photo 7
        caption: ICML 2026 @ Seoul, South Korea (Jul 12, 2026)
      - src: /files/lab_photos/image_91BCE6A7-CCF4-4B8F-A206-9052B3216005_1787755176.jpg
        alt: Lab photo 8
        caption: Julian Mosig von Aehrenfeld's Farewell (Aug 26, 2026)
      - src: /files/lab_photos/image_97AC1C93-C944-4D05-9540-DD65427855B0_1784498830.jpg
        alt: Lab photo 9
        caption: Watching 2026 FIFA World Cup Final @ Billboard Live TAIPEI (Jul 20, 2026)
      - src: /files/lab_photos/image_A0B626D0.jpeg
        alt: Lab photo 10
        caption: Prof. Khoa D Doan Visited NTU (May 20, 2026)
      - src: /files/lab_photos/IMG_1960.jpeg
        alt: Lab photo 11
        caption: Our First Lab Meeting (Feb 25, 2026)
      - src: /files/lab_photos/PXL_20260716_122006292.jpg
        alt: Lab photo 12
        caption: Rishabh Sain's Farewell @ 維傑印度餐廳 (Jul 16, 2026)
      - src: /files/lab_photos/20260225_190445(0).jpg
        alt: Lab photo 13
        caption: Our First Lab Meeting (Feb 25, 2026)
---

<div data-photo-library>
{% for album in albums %}
<h2>{{ album.title | escape }}</h2>
<div class="photo-grid">
{% for photo in album.photos %}
{% include "components/media-item.njk" %}
{% endfor %}
</div>
{% endfor %}
{% include "components/media-viewer.njk" %}
</div>
