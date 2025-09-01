# パッケージマネージャーSpackでCS-PBVRをインストールする方法
## はじめに
CS-PBVRはパッケージマネージャーSpackに対応している。<br>
Spackにはオリジナルのレポジトリを追加する機能があり、それを利用してCS-PBVRをインストールする。

## 公式のSpackと富士通コンパイラ対応のSpackについて
Spackには公式のSpackと富岳などで使用するための富士通コンパイラに対応したSpackが存在する。<br>
富士通コンパイラに対応したSpackは[理化学研究所](https://github.com/RIKEN-RCCS)が公式のSpackをフォークして開発している。<br>
公式のSpackのgithubのレポジトリは[こちら](https://github.com/spack/spack)<br>
富士通コンパイラに対応したSpackのgithubのレポジトリは[こちら](https://github.com/RIKEN-RCCS/spack)<br>
このレポジトリは富士通コンパイラに対応したSpackに使用するオリジナルのレポジトリである。<br>
公式のSpackで使用するオリジナルのレポジトリは[こちら](https://github.com/CCSEPBVR/spack-pbvr-fujitsu)。<br>
ここでは富士通コンパイラに対応したSpackでオリジナルのレポジトリを追加する方法を説明する。

## 公式のSpackにオリジナルのレポジトリを追加する
以下のコマンドでインストールすることができる。<br>
インストール時に使用したコンパイラはgcc@8.5.0もしくはfj@4.12.0
```
spack install gcc@8.5.0 # 必要であれば
git clone https://github.com/CCSEPBVR/spack-pbvr-fujitsu.git # レポジトリのクローン
spack repo add /path/to/spack-pbvr-fujitsu # Spackにレポジトリを追加
spack install pbvr %gcc@8.5.0 # コンパイラgcc@8.5.0を使ってインストール
spack install pbvr %fj@4.12.0 # コンパイラfj@4.12.0を使ってインストール 
```
インストール時にオプションを設定することができる。<br>
すべてのオプションがデフォルトでONになっている。<br>
富士通コンパイラ(fj@4.12.0)は現在client, extended_fileformatに対応していない。
- client：クライアントをビルドする
- mpi：MPI並列化を有効にする
- extended_fileformat：データ形式拡張(VTK)を有効にする

オプションの設定方法のサンプルは以下の通り。
```
spack install pbvr +client +mpi +extended_fileformat %gcc@8.5.0 # すべて有効(デフォルト)
spack install pbvr ~client ~mpi ~extended_fileformat %gcc@8.5.0 # すべて無効
```