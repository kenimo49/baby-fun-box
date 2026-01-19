# Shared - 共有ライブラリ

このディレクトリには、複数のゲームで共有されるユーティリティやコンポーネントが格納されています。

## ディレクトリ構造

```
shared/
├── __init__.py
├── utils/              # ユーティリティ関数
├── components/         # 再利用可能なコンポーネント
└── constants.py        # 共通定数
```

## 使用方法

```python
from shared.utils import ...
from shared.components import ...
```
