# CBC-data

Chinese Buddhist Canon data to be imported on the BUDA platform

This repository aggregates data from various sources and combines it in a form that then will be serialized in RDF.

The repository will focus first only on the Taisho edition, specifically on the text in the first 55 volumes (up to T2184 included) and volume 85.

Data in the Public domain, gathered from the following sources:
- *Répertoire du Canon Bouddhique Sino-Japonais, Fascicule annexe du Hōbōgirin*, compilé par Paul Demiéville, Paris, Tokyo, 1978
- *The Korean Buddhist Canon: A Descriptive Catalogue*, Lewis R. Lancaster, 1974 ([electronic version by A. Charles Muller](http://www.acmuller.net/descriptive_catalogue/))
- *Resources for Kanjur and Tanjur studies* ([website](https://www.istb.univie.ac.at/kanjur/rktsneu/sub/index.php), [github](https://github.com/brunogml/rKTs))
- *CBETA* \[Chinese Buddhist Electronic Text Association\]. Taishō shinshū daizōkyō 大正新脩大藏經. Edited by Takakusu Junjirō 高楠順次郎 and Watanabe Kaigyoku 渡邊海旭. Tokyo: Taishō shinshū daizōkyō kankōkai/Daizō shuppan, 1924-1932. CBReader, 2019
- *The Nyingma Edition of the sDe-dge bKa'-'gyur and bsTan-'gyur Research Catalogue and Bibliography*, Published by Dharma Mudranālaya under the direction of Tarthang Tulku, Oakland, 1977-1983 (BDRC [W4CZ7370](http://tbrc.org/link?RID=W4CZ7370)) 
- *Chinese Sūtras in Tibetan Translation: A Preliminary Survey*, Annual Report of The International Research Institute for Advanced Buddhology at Soka University, 2019, on [ResearchGate](https://www.academia.edu/40447816/Chinese_S%C5%ABtras_in_Tibetan_Translation_A_Preliminary_Survey)


## Running

```
python3 derive.py
python3 create-lod.py
curl -X PUT -H Content-Type:text/turtle -T CBC.ttl -G http://buda1.bdrc.io:13180/fuseki/corerw/data --data-urlencode 'graph=http://purl.bdrc.io/graph/CBC-data'
```