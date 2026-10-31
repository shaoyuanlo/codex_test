---
layout: layouts/page.njk
section: photos
permalink: /photos/index.html
title: Photos
albums:
  - title: "2026"
    photos:
      - src: /files/lab_photos/image_2F33A832.jpeg
        alt: Lab photo 1
        caption: Add a caption for this photo.
      - src: /files/lab_photos/IMG_6450.jpg
        alt: Lab photo 2
        caption: Add a caption for this photo.
      - src: /files/lab_photos/PXL_20260710_095915324.jpg
        alt: Lab photo 3
        caption: Add a caption for this photo.
      - src: /files/lab_photos/PXL_20260710_103414851.jpg
        alt: Lab photo 4
        caption: Add a caption for this photo.
      - src: /files/lab_photos/PXL_20260715_124218569.jpg
        alt: Lab photo 5
        caption: Add a caption for this photo.
      - src: /files/lab_photos/image_71B54162.jpeg
        alt: Lab photo 6
        caption: Add a caption for this photo.
  - title: "More Photos"
    photos:
      - src: /files/lab_photos/image_72910324.jpg
        alt: Lab photo 7
        caption: Add a caption for this photo.
      - src: /files/lab_photos/image_91BCE6A7-CCF4-4B8F-A206-9052B3216005_1787755176.jpg
        alt: Lab photo 8
        caption: Add a caption for this photo.
      - src: /files/lab_photos/image_97AC1C93-C944-4D05-9540-DD65427855B0_1784498830.jpg
        alt: Lab photo 9
        caption: Add a caption for this photo.
      - src: /files/lab_photos/image_A0B626D0.jpeg
        alt: Lab photo 10
        caption: Add a caption for this photo.
      - src: /files/lab_photos/IMG_1960.jpeg
        alt: Lab photo 11
        caption: Add a caption for this photo.
      - src: /files/lab_photos/PXL_20260716_122006292.jpg
        alt: Lab photo 12
        caption: Add a caption for this photo.
      - src: /files/lab_photos/Trai_lab3.mp4
        type: video
        poster: /files/lab_photos/Trai_lab3-poster.jpg
        alt: Lab video
        caption: Add a caption for this video.
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
