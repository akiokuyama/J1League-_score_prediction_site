# archive ディレクトリ構成

`archive/` は、現在のアプリ運用やGitHub Actionsでは直接使わない旧分析資産の保管場所です。

```text
archive/
├── notebooks/          # 旧Notebook資産
└── legacy_rawdata/     # 旧Notebook由来のRawData CSV
```

現行パイプラインでは、データ取得・加工は主に `Data/raw/`、`Data/processed/`、`Data/features/` を使用します。
