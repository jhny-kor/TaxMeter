# Korea Tax Ontology 2026

기준일: 2026-05-02

대한민국 세금 온톨로지는 앱 코드와 분리된 Obsidian vault로 구현한다. 원본
정의는 `ontology/scripts/generate_vault.py`에 있으며, 생성 결과는
`ontology/vault`의 Markdown 노트와 `ontology/exports/korea-tax-ontology-2026.json`
으로 나온다.

## 산출물

- `ontology/vault`: Obsidian에서 열 수 있는 학습용 vault.
- `ontology/schema/node.schema.json`: 노드 frontmatter 구조.
- `ontology/scripts/generate_vault.py`: 공식 출처, 항목 매니페스트, 노트 생성기.
- `ontology/scripts/validate_ontology.py`: 누락 항목, 설명, 출처, 링크 무결성 검증기.
- `ontology/exports/korea-tax-ontology-2026.json`: 앱이나 다른 도구에서 쓸 수 있는 export.

## 구현 범위

- 국세: 국세기본법 제2조가 열거한 국세 세목 12개 전체.
- 관세: 관세법 제14조 기준 별도 관세 영역.
- 지방세: 지방세기본법 제8조 기준 지방세 세목 11개 전체.
- 공제·감면: 국세청 연말정산 계산 구조의 소득공제, 세액공제, 세액감면
  상위 구조와 주요 하위 항목.
- 법인세 조세지원: 국세청 법인세 공제감면 안내의 지원제도 28개.
- 정책지원금·세제지원 계좌: 근로장려금, 자녀장려금, 청년도약계좌, ISA.
- 기한: 종합소득세 확정신고, 연말정산, 원천세, 부가가치세, 근로·자녀장려금
  신청/지급 기한.
- 용어: 국세, 지방세, 세법, 원천징수, 과세기간, 과세표준, 법정신고기한,
  소득공제, 세액공제, 세액감면, 총소득, 총급여액 등, 재산요건,
  간이과세자, 기한의 특례, 관세.

## 완전성 검증

검증 명령:

```sh
python3 ontology/scripts/validate_ontology.py
```

검증 기준:

- 모든 국세 세목 12개가 존재한다.
- 모든 지방세 세목 11개가 존재한다.
- 국세청 법인세 공제감면 지원제도 28개가 존재한다.
- 각 항목은 설명과 공식/법률 출처를 가진다.
- `parents`, `children`, `related`, `terms`, `deadlines`, `sources`가 실제 노트를
  가리킨다.
- 부모/자식 연결이 양방향이다.

## 공식 출처

- 국세기본법 제2조:
  https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900637068
- 지방세기본법 제8조:
  https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000903169
- 관세법 제14조:
  https://law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900015991
- 연말정산 세액계산방법:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7870&mi=2312
- 근로소득 과세표준과 산출세액:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7873&mi=6594
- 근로소득 특별세액공제:
  https://kids.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7874&mi=6438
- 법인세 공제감면:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7987&mi=6561
- 근로장려금·자녀장려금:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7781&mi=2450
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7782&mi=2451
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&mi=2452
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&mi=2453
- 2026년 국세청 세무일정:
  https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?mi=135747&taxYear=2026
- 청년도약계좌:
  https://ylaccount.kinfa.or.kr/main
- ISA 정책문답:
  https://www.fsc.go.kr/po020201/27339
