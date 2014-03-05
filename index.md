---
layout: default
title: 近文庫alpha
---

<ul>
{% for post in site.posts %}
  <li>
    <a href="{{ post.url }}">{{ post.date | date_to_long_string }} : {{ post.title }}</a>
    <p>{{ post.excerpt }}</p>
  </li>
{% endfor %}
</ul>


# 近デジファイル減量の試み

## 概要

## 目的
  近代デジタルライブラリー(以下、近デジ)のファイルを一冊の本ごとにひとつのファイルとし
  それをタブレットにいれ手軽に読めるようにすること

## 実現したいこと

* file sizeを小さくすること
* 読みやすい画面を得ること
 - タブレットの画面に一ページを無駄なく表示すること
 - ノイズを削除すること

    
## やったこと

* download file
* 画像処理による文字の抽出と整列
* opencv + python
  - 先行事例
  - 練習
  - 使えそうな処理の調査
  - 処理方法の決定
  - 実装
  - 文字認識とエンコード
    + 可能な範囲で市販のOCRソフトを利用
    + 認識できない文字は画像をそのまま使用
* 一冊の本のファイル化
  - kindle
  - epub
  - pdf

* ライセンスと公開と販売
  - toolの公開
  - NDLの方針
  - オープンデータ
  - クリエイティブコモンズ
* まとめ
* 課題
  - OCR精度の向上
  - Social OCRのとりくみ
