#!/usr/bin/env python3
"""Generate the standalone OpenTax Obsidian vault.

The generated Markdown files are intentionally separate from the TaxMeter app.
Obsidian is the human-facing study surface; the frontmatter is the machine-
readable ontology surface.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "vault"
EXPORT_PATH = ROOT / "exports" / "korea-tax-ontology-2026.json"
CUSTOM_ITEMS_PATH = ROOT / "custom" / "items.json"


SOURCES = {
    "source.national-tax-framework-act.2026.article2": {
        "title": "국세기본법 제2조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900637068",
        "basis_date": "시행 2026-01-01",
        "description": "국세 세목, 세법, 원천징수, 과세기간, 과세표준 등 국세 기본 용어의 법률상 근거입니다.",
    },
    "source.local-tax-framework-act.2026.article8": {
        "title": "지방세기본법 제8조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000903169",
        "basis_date": "시행 2026-02-05",
        "description": "특별시세, 광역시세, 도세, 구세, 시·군세, 특별자치시·특별자치도세의 세목 근거입니다.",
    },
    "source.customs-act.2026.article14": {
        "title": "관세법 제14조",
        "publisher": "국가법령정보센터",
        "url": "https://law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900015991",
        "basis_date": "시행 2026-01-01",
        "description": "수입물품에 관세를 부과한다는 관세의 과세물건 근거입니다.",
    },
    "source.nts.year-end-settlement.calculation": {
        "title": "연말정산 세액계산방법",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7870&mi=2312",
        "basis_date": "2026-05-02 확인",
        "description": "연말정산 계산 단계와 인적공제, 연금보험료공제, 특별소득공제, 세액감면, 세액공제의 구조 근거입니다.",
    },
    "source.nts.year-end-settlement.deduction-limit": {
        "title": "근로소득 과세표준과 산출세액",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7873&mi=6594",
        "basis_date": "2026-05-02 확인",
        "description": "소득공제 종합한도와 종합한도 적용 특별소득공제 등 항목의 근거입니다.",
    },
    "source.nts.year-end-settlement.special-credit": {
        "title": "근로소득 특별세액공제",
        "publisher": "국세청",
        "url": "https://kids.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7874&mi=6438",
        "basis_date": "2026-05-02 확인",
        "description": "보험료, 의료비, 교육비, 기부금 등 특별세액공제 항목의 근거입니다.",
    },
    "source.nts.housing-rent-principal-deduction": {
        "title": "주택임차차입금 원리금 상환액 소득공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239021&mi=40629",
        "basis_date": "2026-05-03 확인",
        "description": "주택임차차입금 원리금 상환액의 공제대상자, 주택요건, 40% 공제율, 연 400만원 한도 근거입니다.",
    },
    "source.nts.housing-mortgage-interest-deduction": {
        "title": "장기주택저당차입금 이자상환액 소득공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239020&mi=40630",
        "basis_date": "2026-05-03 확인",
        "description": "장기주택저당차입금 이자상환액의 상환기간·상환방식별 600만원~2,000만원 한도 근거입니다.",
    },
    "source.nts.housing-savings-deduction": {
        "title": "주택마련저축 소득공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239022&mi=40610",
        "basis_date": "2026-05-03 확인",
        "description": "총급여 7,000만원 이하 무주택 세대주·배우자의 주택마련저축 납입액 40%, 연 납입액 300만원 한도 근거입니다.",
    },
    "source.nts.sme-employment-income-reduction": {
        "title": "중소기업 취업자 소득세 감면",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239023&mi=40611",
        "basis_date": "2026-05-03 확인",
        "description": "청년, 고령자, 장애인, 경력단절근로자별 감면기간, 감면율, 과세기간별 200만원 감면한도 근거입니다.",
    },
    "source.nts.education-expense-credit": {
        "title": "교육비 세액공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239024&mi=40612",
        "basis_date": "2026-05-03 확인",
        "description": "교육비 세액공제의 본인 전액, 취학전·초중고 300만원, 대학생 900만원, 장애인 특수교육비 전액 한도와 15% 공제율 근거입니다.",
    },
    "source.nts.donation-credit": {
        "title": "기부금 세액공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239040&mi=40978",
        "basis_date": "2026-05-03 확인",
        "description": "정치자금, 고향사랑, 특례, 우리사주조합, 일반기부금의 공제율과 금액 구간 근거입니다.",
    },
    "source.nts.corporate-tax-consulting.2026": {
        "title": "중소기업 공제·감면 컨설팅 제도 안내",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239070&mi=41093",
        "basis_date": "2026-05-03 확인",
        "description": "2026년 창업중소기업 세액감면, 중소기업특별세액감면, 통합투자세액공제 등 주요 공제·감면율 근거입니다.",
    },
    "source.nts.monthly-rent-credit": {
        "title": "월세액 세액공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239025",
        "basis_date": "2026-05-02 확인",
        "description": "월세액 세액공제의 총급여, 종합소득금액, 주택, 전입신고, 한도 조건 근거입니다.",
    },
    "source.nts.credit-card-deduction": {
        "title": "신용카드 등 사용금액 소득공제",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7794&mi=2202",
        "basis_date": "2026-05-02 확인",
        "description": "신용카드, 직불카드, 현금영수증 사용액 소득공제와 총급여 25% 기준의 근거입니다.",
    },
    "source.nts.income-tax.deadline": {
        "title": "종합소득세 신고납부기한",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7665&mi=2225",
        "basis_date": "2026-05-02 확인",
        "description": "2025년 귀속 종합소득세 신고·납부 기한과 기한의 특례 근거입니다.",
    },
    "source.nts.income-tax.rates": {
        "title": "종합소득세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7667&mi=2223",
        "basis_date": "2026-05-02 확인",
        "description": "2023~2025년 귀속 종합소득세 과세표준 구간, 세율, 누진공제액 근거입니다.",
    },
    "source.nts.vat.overview": {
        "title": "부가가치세 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7693&mi=2272",
        "basis_date": "2026-05-02 확인",
        "description": "부가가치세 구조와 일반과세자·간이과세자 구분 기준의 근거입니다.",
    },
    "source.nts.vat.filing-duty": {
        "title": "부가가치세 신고·납부 의무",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7806",
        "basis_date": "2026-05-02 확인",
        "description": "일반과세자와 간이과세자의 과세기간, 확정신고 납부기한, 간이과세자 예정신고 및 납부면제 기준 근거입니다.",
    },
    "source.nts.business-registration.application": {
        "title": "사업자등록 신청",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7777&mi=2444",
        "basis_date": "2026-05-02 확인",
        "description": "신규사업자 사업자등록, 일반과세자·간이과세자 유형 선택, 간이과세 배제 업종 확인 근거입니다.",
    },
    "source.nts.withholding.overview": {
        "title": "원천징수 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7701&mi=2289",
        "basis_date": "2026-05-02 확인",
        "description": "원천징수 제도, 원천징수의무자, 원천징수세액 납세지와 신고·납부 흐름 근거입니다.",
    },
    "source.nts.business-income.withholding": {
        "title": "사업소득 원천징수",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7902&mi=6466",
        "basis_date": "2026-05-02 확인",
        "description": "원천징수 대상 사업소득, 3% 원천징수, 다음 달 10일 또는 반기 마지막 달 다음 달 10일 납부 흐름 근거입니다.",
    },
    "source.nts.capital-gains.overview": {
        "title": "양도소득세 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7709&mi=2308",
        "basis_date": "2026-05-02 확인",
        "description": "양도소득세 세액계산 흐름, 부동산·주식 양도차익 계산, 기본공제와 가산세 흐름 근거입니다.",
    },
    "source.nts.capital-gains.deadline": {
        "title": "양도소득세 신고납부기한",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7713&mi=2371",
        "basis_date": "2026-05-02 확인",
        "description": "토지·건물·부동산 권리·기타자산, 주식·출자지분 양도의 예정신고와 다음연도 5월 확정신고 기한 근거입니다.",
    },
    "source.nts.capital-gains.rates": {
        "title": "양도소득세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7711&mi=2312",
        "basis_date": "2026-05-02 확인",
        "description": "양도소득세 기본세율, 보유기간·자산 유형별 세율, 국외주식·파생상품 세율 근거입니다.",
    },
    "source.nts.capital-gains.basic-deduction": {
        "title": "양도소득 기본공제 신고서식",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/tax/sub/1.2.3.%EC%96%91%EB%8F%84%EC%86%8C%EB%93%9D%EA%B3%BC%EC%84%B8%ED%91%9C%EC%A4%80%20%EC%8B%A0%EA%B3%A0%20%EB%B0%8F%20%EB%82%A9%EB%B6%80%EA%B3%84%EC%82%B0%EC%84%9C.html",
        "basis_date": "2026-05-03 확인",
        "description": "양도소득기본공제가 국내 부동산, 국내 주식 등, 국외 부동산, 국외 주식 등, 파생상품별로 각각 2,500,000원 적용된다는 신고서식 근거입니다.",
    },
    "source.nts.inheritance.overview": {
        "title": "상속세 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7719&mi=2324",
        "basis_date": "2026-05-02 확인",
        "description": "상속세 신고납부기한, 거주자 6개월·비거주자 9개월 기한과 제출서류 흐름 근거입니다.",
    },
    "source.nts.gift.deadline": {
        "title": "증여세 신고납부기한",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7727&mi=2339",
        "basis_date": "2026-05-02 확인",
        "description": "일반 증여와 증여의제 유형별 법정신고기한과 증여세 신고 제출서류 흐름 근거입니다.",
    },
    "source.nts.inheritance.rates": {
        "title": "상속세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7957&mi=6529",
        "basis_date": "2026-05-02 확인",
        "description": "상속세 과세표준 5단계 초과누진세율과 누진공제액 근거입니다.",
    },
    "source.nts.gift.rates": {
        "title": "증여세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7960&mi=2227",
        "basis_date": "2026-05-02 확인",
        "description": "증여세 과세표준 5단계 초과누진세율, 세대생략 할증, 창업자금·가업승계 특례세율 근거입니다.",
    },
    "source.nts.comprehensive-real-estate.overview": {
        "title": "종합부동산세 개요",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7733&mi=2351",
        "basis_date": "2026-05-02 확인",
        "description": "매년 6월 1일 과세기준일, 주택·종합합산토지·별도합산토지 공제금액과 재산세-종합부동산세 연결 구조 근거입니다.",
    },
    "source.nts.comprehensive-real-estate.rates": {
        "title": "종합부동산세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7736&mi=40378",
        "basis_date": "2026-05-02 확인",
        "description": "2023년 이후 주택, 종합합산토지, 별도합산토지의 종합부동산세 과세표준 구간별 세율 근거입니다.",
    },
    "source.nts.real-estate-tax.faq": {
        "title": "궁금해요 종합부동산 세법",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7739&mi=2357",
        "basis_date": "2026-05-02 확인",
        "description": "종합부동산세 과세표준 계산식, 공정시장가액비율, 재산세 표준세율, 세액공제와 세부담상한 근거입니다.",
    },
    "source.nts.corporate-tax.rates": {
        "title": "법인세 세율",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7746",
        "basis_date": "2026-05-02 확인",
        "description": "2026.1.1. 이후 개시 사업연도 법인세 각 사업연도 소득 과세표준 구간, 세율, 누진공제액 근거입니다.",
    },
    "source.nts.corporate-tax.reliefs": {
        "title": "법인세 공제감면",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7987&mi=6561",
        "basis_date": "2026-05-02 확인",
        "description": "중소기업, 모든 기업, 법인세법상 공제·감면과 과세이연 지원제도의 공식 목록 근거입니다.",
    },
    "source.nts.eitc.intro": {
        "title": "근로장려금 소개",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7781&mi=2450",
        "basis_date": "2026-05-02 확인",
        "description": "근로장려금 제도 취지, 가구 유형별 소득 기준, 최대지급액 근거입니다.",
    },
    "source.nts.ctc.intro": {
        "title": "자녀장려금 소개",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7782&mi=2451",
        "basis_date": "2026-05-02 확인",
        "description": "자녀장려금의 부양자녀, 총소득, 자녀 1인당 지급액 근거입니다.",
    },
    "source.nts.grant.eligibility": {
        "title": "근로·자녀장려금 신청자격",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&mi=2452",
        "basis_date": "2026-05-02 확인",
        "description": "2025년 소득요건, 2025년 6월 1일 재산요건, 신청제외자 기준의 근거입니다.",
    },
    "source.nts.grant.deadline": {
        "title": "근로·자녀장려금 심사 및 지급",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&mi=2453",
        "basis_date": "2026-05-02 확인",
        "description": "정기신청분, 기한 후 신청분, 반기신청분의 심사와 지급기한 근거입니다.",
    },
    "source.nts.grant.2026-regular-press": {
        "title": "2026년 근로·자녀장려금 정기신청 보도자료",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/na/ntt/selectNttInfo.do?mi=2201&nttSn=1350768",
        "basis_date": "2026-04-30",
        "description": "2025년 귀속 근로·자녀장려금 소득요건, 재산요건, 감액구간, 정기 신청·지급 일정 근거입니다.",
    },
    "source.nts.tax-calendar.2026": {
        "title": "2026년 국세청 세무일정",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?mi=135747&taxYear=2026",
        "basis_date": "2026-05-02 확인",
        "description": "월별 신고·납부 일정과 기한의 특례 확인용 공식 일정입니다.",
    },
    "source.govkr.basic-livelihood-benefit": {
        "title": "생계급여",
        "publisher": "정부24",
        "url": "https://www.gov.kr/portal/service/serviceInfo/WII000001410",
        "basis_date": "최종수정일 2026-02-09",
        "description": "2026년 생계급여 선정·급여기준, 기준 중위소득 32%, 가구원 수별 급여기준, 부양의무자 제외 기준 근거입니다.",
    },
    "source.fsc.youth-future-savings": {
        "title": "청년미래적금 카드뉴스",
        "publisher": "금융위원회",
        "url": "https://www.fsc.go.kr/no040101?cnId=2983",
        "basis_date": "2025-12-11",
        "description": "2026년 6월 출시 예정 청년미래적금의 가입 소득기준, 만기, 월 납입한도, 정부기여금 매칭비율, 비과세 특례 근거입니다.",
    },
    "source.kinfa.illegal-private-finance-prevention-loan": {
        "title": "불법사금융예방대출",
        "publisher": "서민금융진흥원",
        "url": "https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do",
        "basis_date": "2026-05-02 확인",
        "description": "신용평점 하위 20%·연소득 3,500만원 이하 대상 생계비 정책서민금융상품의 대출한도, 금리, 상환방식 근거입니다.",
    },
    "source.kinfa.hessal-loan-youth": {
        "title": "햇살론유스",
        "publisher": "서민금융진흥원",
        "url": "https://www.kinfa.or.kr/financialProduct/hessalLoanYoos.do",
        "basis_date": "2026-05-02 확인",
        "description": "만 19~34세 청년·대학생·사회초년생 대상 햇살론유스의 소득요건, 동일인 한도, 연간·용도별 보증한도 근거입니다.",
    },
    "source.kinfa.hessal-119": {
        "title": "햇살론119",
        "publisher": "서민금융진흥원",
        "url": "https://www.kinfa.or.kr/financialProduct/hessalLoanEmergency.do",
        "basis_date": "2026-05-02 확인",
        "description": "은행권 채무조정 프로그램을 성실상환 중인 영세 개인사업자 대상 신규 운전자금 보증부 대출의 지원요건과 한도 근거입니다.",
    },
    "source.kinfa.youth-leap": {
        "title": "청년도약계좌 상품 안내",
        "publisher": "서민금융진흥원",
        "url": "https://ylaccount.kinfa.or.kr/main",
        "basis_date": "2026-05-02 확인",
        "description": "청년도약계좌 가입 연령, 개인소득, 가구소득, 금융소득종합과세 이력 제한 근거입니다.",
    },
    "source.hf.didimdol-loan": {
        "title": "내집마련 디딤돌대출 상품소개",
        "publisher": "한국주택금융공사",
        "url": "https://www.hf.go.kr/ko/sub01/sub01_02_01.do",
        "basis_date": "2026-05-02 확인",
        "description": "디딤돌대출의 무주택, 순자산, 주택가격, 부부합산 연소득, LTV·DTI, 대출한도 기준 근거입니다.",
    },
    "source.hf.didimdol-rate.2026-05": {
        "title": "2026년 5월 디딤돌대출 금리안내",
        "publisher": "한국주택금융공사",
        "url": "https://hf.go.kr/ko/sub01/sub01_02_03.do",
        "basis_date": "공시일 2026-05-01",
        "description": "2026년 5월 기준 디딤돌대출 소득구간별 만기 금리와 우대금리 근거입니다.",
    },
    "source.hf.special-rent-guarantee": {
        "title": "특례전세자금보증",
        "publisher": "한국주택금융공사",
        "url": "https://www.hf.go.kr/ko/sub02/sub02_01_04.do",
        "basis_date": "2026-05-02 확인",
        "description": "무주택 청년, 다자녀가구, 정책서민금융 이용자 등 특례전세자금보증 대상별 보증요건과 보증한도 근거입니다.",
    },
    "source.ccrs.long-term-delinquent-debt-adjustment": {
        "title": "장기연체자 특별채무조정",
        "publisher": "신용회복위원회",
        "url": "https://ad.ccrs.or.kr/cms/com/index.do?CONTENTS_NO=2&MENU_ID=1580",
        "basis_date": "2026-05-02 확인",
        "description": "새도약기금 관련 5년 이상 장기연체채권 특별채무조정의 2026년 기준중위소득 125%, 채무감면, 분할상환, 상환유예 근거입니다.",
    },
    "source.nts.retirement-income.calculation": {
        "title": "퇴직소득세 계산방법",
        "publisher": "국세청",
        "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7880&mi=6444",
        "basis_date": "2026-05-03 확인",
        "description": "퇴직소득금액, 근속연수공제, 환산급여, 환산급여공제, 과세표준, 환산산출세액, 산출세액 계산 구조와 근속연수별 공제금액 근거입니다.",
    },
    "source.fsc.isa.policy": {
        "title": "ISA 정책문답",
        "publisher": "금융위원회",
        "url": "https://www.fsc.go.kr/po020201/27339",
        "basis_date": "2026-05-02 확인",
        "description": "개인종합자산관리계좌(ISA)의 연 2,000만원 납입한도, 순소득 200만원 비과세, 초과분 분리과세 등 세제지원과 가입 제한을 이해하기 위한 정책 근거입니다.",
    },
    "source.moef.isa.tax-benefit": {
        "title": "ISA 세제혜택 설명",
        "publisher": "기획재정부·대한민국 정책브리핑",
        "url": "https://www.korea.kr/briefing/actuallyView.do?newsId=148874193",
        "basis_date": "2026-05-03 확인",
        "description": "ISA 계좌 순소득 200만원, 서민·농어민형 400만원 비과세와 초과분 9% 저율 분리과세 근거입니다.",
    },
    "source.law.local-tax-act.rates": {
        "title": "지방세법 세율 조문",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/지방세법",
        "basis_date": "2026-05-03 확인",
        "description": "취득세, 등록면허세, 레저세, 담배소비세, 지방소비세, 주민세, 지방소득세, 자동차세, 지역자원시설세, 지방교육세의 세율·세액 산식 근거입니다.",
    },
    "source.law.stamp-tax-act.article3": {
        "title": "인지세법 제3조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/인지세법/제3조",
        "basis_date": "2026-05-03 확인",
        "description": "과세문서와 문서 기재금액별 인지세액 근거입니다.",
    },
    "source.law.securities-transaction-tax-act.article8": {
        "title": "증권거래세법 제8조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/증권거래세법/제8조",
        "basis_date": "2026-05-03 확인",
        "description": "주권 양도 시 증권거래세 과세표준과 세율 적용 근거입니다.",
    },
    "source.law.education-tax-act.article5": {
        "title": "교육세법 제5조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/교육세법/제5조",
        "basis_date": "2026-05-03 확인",
        "description": "교육세 과세표준과 세율 근거입니다.",
    },
    "source.law.special-rural-development-tax-act.article5": {
        "title": "농어촌특별세법 제5조",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/농어촌특별세법/제5조",
        "basis_date": "2026-05-03 확인",
        "description": "농어촌특별세 과세표준과 세율 근거입니다.",
    },
    "source.law.individual-consumption-tax-act.rates": {
        "title": "개별소비세법 세율 조문",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/개별소비세법",
        "basis_date": "2026-05-03 확인",
        "description": "과세물품, 과세장소, 과세유흥장소, 영업행위별 개별소비세 세율과 정액세 근거입니다.",
    },
    "source.law.transport-energy-environment-tax-act.rates": {
        "title": "교통·에너지·환경세법 세율 조문",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/교통ㆍ에너지ㆍ환경세법",
        "basis_date": "2026-05-03 확인",
        "description": "휘발유, 경유 등 과세물품별 교통·에너지·환경세 정액세율 근거입니다.",
    },
    "source.law.liquor-tax-act.rates": {
        "title": "주세법 세율 조문",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/주세법",
        "basis_date": "2026-05-03 확인",
        "description": "주류 종류별 주세 종가세·종량세 세율 근거입니다.",
    },
    "source.law.customs-tariff": {
        "title": "관세법 관세율표",
        "publisher": "국가법령정보센터",
        "url": "https://www.law.go.kr/법령/관세법/별표",
        "basis_date": "2026-05-03 확인",
        "description": "수입물품 품목분류별 관세율표와 품목별 세율 적용 근거입니다.",
    },
}


NATIONAL_TAX_IDS = [
    "tax.income",
    "tax.corporate",
    "tax.inheritance-and-gift",
    "tax.comprehensive-real-estate",
    "tax.value-added",
    "tax.individual-consumption",
    "tax.transport-energy-environment",
    "tax.liquor",
    "tax.stamp",
    "tax.securities-transaction",
    "tax.education",
    "tax.special-rural-development",
]

LOCAL_TAX_IDS = [
    "local.acquisition",
    "local.registration-license",
    "local.leisure",
    "local.tobacco-consumption",
    "local.local-consumption",
    "local.resident",
    "local.local-income",
    "local.property",
    "local.automobile",
    "local.regional-resource-facility",
    "local.local-education",
]

CORPORATE_SUPPORT_IDS = [
    "corporate.support.startup-sme-reduction",
    "corporate.support.sme-special-reduction",
    "corporate.support.tech-transfer-reduction",
    "corporate.support.winwin-payment-credit",
    "corporate.support.wage-increase-credit",
    "corporate.support.performance-sharing-credit",
    "corporate.support.employment-maintenance-credit",
    "corporate.support.social-insurance-credit",
    "corporate.support.minimum-tax-preference",
    "corporate.support.cooperation-credit",
    "corporate.support.rnd-credit",
    "corporate.support.rnd-grant-deferral",
    "corporate.support.rnd-zone-reduction",
    "corporate.support.ma-credit",
    "corporate.support.facility-investment-credit",
    "corporate.support.local-relocation-reduction",
    "corporate.support.agricultural-corporation-reduction",
    "corporate.support.industrial-complex-reduction",
    "corporate.support.social-enterprise-reduction",
    "corporate.support.jeju-zone-reduction",
    "corporate.support.enterprise-city-reduction",
    "corporate.support.e-filing-credit",
    "corporate.support.restructuring-deferral",
    "corporate.support.local-relocation-deferral",
    "corporate.support.good-landlord-credit",
    "corporate.support.crisis-area-startup-reduction",
    "corporate.support.disaster-loss-credit",
    "corporate.support.foreign-tax-paid-credit",
]


def node(
    id_: str,
    title: str,
    type_: str,
    description: str,
    folder: str,
    *,
    basis_year: int | None = 2026,
    effective_date: str | None = None,
    expiration_date: str | None = None,
    parents: list[str] | None = None,
    children: list[str] | None = None,
    related: list[str] | None = None,
    terms: list[str] | None = None,
    deadlines: list[str] | None = None,
    sources: list[str] | None = None,
    criteria: list[dict] | None = None,
    law_reference: str = "",
    tags: list[str] | None = None,
) -> dict:
    item = {
        "id": id_,
        "title": title,
        "type": type_,
        "description": description,
        "folder": folder,
        "basis_year": basis_year,
        "effective_date": effective_date,
        "expiration_date": expiration_date,
        "parents": parents or [],
        "children": children or [],
        "related": related or [],
        "terms": terms or [],
        "deadlines": deadlines or [],
        "sources": sources or [],
        "law_reference": law_reference,
        "tags": tags or [],
    }
    if criteria:
        item["criteria"] = criteria
    return item


def national_tax(id_: str, title: str, description: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.national-tax-framework-act.2026.article2"])
    terms = kwargs.pop("terms", ["term.national-tax", "term.tax-law"])
    tags = kwargs.pop("tags", ["national-tax"])
    return node(
        id_,
        title,
        "tax",
        description,
        "10_Taxes/National",
        parents=["category.national-taxes"],
        sources=sources,
        effective_date="2026-01-01",
        law_reference="국세기본법 제2조 제1호",
        terms=terms,
        tags=tags,
        **kwargs,
    )


def local_tax(id_: str, title: str, description: str, parent: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.local-tax-framework-act.2026.article8"])
    terms = kwargs.pop("terms", ["term.local-tax"])
    tags = kwargs.pop("tags", ["local-tax"])
    return node(
        id_,
        title,
        "tax",
        description,
        "10_Taxes/Local",
        parents=[parent],
        sources=sources,
        effective_date="2026-02-05",
        law_reference="지방세기본법 제8조",
        terms=terms,
        tags=tags,
        **kwargs,
    )


def deduction(id_: str, title: str, description: str, parent: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.year-end-settlement.calculation"])
    terms = kwargs.pop("terms", ["term.income-deduction", "term.tax-base"])
    tags = kwargs.pop("tags", ["income-deduction"])
    if "criteria" not in kwargs:
        criteria = globals().get("DEDUCTION_CRITERIA_BY_ID", {}).get(id_)
        if criteria:
            kwargs["criteria"] = criteria
    return node(
        id_,
        title,
        "deduction",
        description,
        "20_Deductions/IncomeDeductions",
        parents=[parent],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


def credit(id_: str, title: str, description: str, parent: str = "category.tax-credits", **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.year-end-settlement.special-credit"])
    terms = kwargs.pop("terms", ["term.tax-credit"])
    tags = kwargs.pop("tags", ["tax-credit"])
    if "criteria" not in kwargs:
        criteria = globals().get("CREDIT_CRITERIA_BY_ID", {}).get(id_)
        if criteria:
            kwargs["criteria"] = criteria
    return node(
        id_,
        title,
        "tax-credit",
        description,
        "20_Deductions/TaxCredits",
        parents=[parent],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


def corporate_support(id_: str, title: str, description: str, **kwargs) -> dict:
    sources = kwargs.pop("sources", ["source.nts.corporate-tax.reliefs"])
    terms = kwargs.pop("terms", ["term.tax-credit", "term.tax-reduction"])
    tags = kwargs.pop("tags", ["corporate-tax-support"])
    if "criteria" not in kwargs:
        criteria = globals().get("CORPORATE_SUPPORT_CRITERIA_BY_ID", {}).get(id_)
        if criteria:
            kwargs["criteria"] = criteria
    return node(
        id_,
        title,
        "corporate-tax-support",
        description,
        "20_Deductions/CorporateTaxSupports",
        parents=["category.corporate-tax-supports"],
        sources=sources,
        terms=terms,
        tags=tags,
        **kwargs,
    )


TERMS = {
    "term.national-tax": ("국세", "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.local-tax": ("지방세", "지방자치단체가 과세권을 가지며 지방세기본법상 세목과 자치단체 세목 배분에 따라 관리되는 세금입니다.", ["source.local-tax-framework-act.2026.article8"]),
    "term.tax-law": ("세법", "국세의 종목과 세율을 정하는 법률과 국세기본법이 세법으로 묶는 관련 법률 체계입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.withholding": ("원천징수", "소득을 지급하는 자가 세법에 따라 세금을 미리 징수해 납부하는 방식입니다.", ["source.national-tax-framework-act.2026.article2", "source.nts.year-end-settlement.calculation"]),
    "term.tax-period": ("과세기간", "세법에 따라 과세표준 계산의 기초가 되는 기간입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.tax-base": ("과세표준", "세율 적용과 세액 산출의 기준이 되는 과세대상의 수량 또는 가액입니다.", ["source.national-tax-framework-act.2026.article2", "source.nts.year-end-settlement.calculation"]),
    "term.tax-rate": ("세율", "과세표준 또는 공급가액 등에 적용해 산출세액을 계산하는 비율입니다.", ["source.nts.income-tax.rates", "source.nts.corporate-tax.rates"]),
    "term.progressive-deduction": ("누진공제", "초과누진세율 구조에서 산출세액을 과세표준 × 세율 - 누진공제액 방식으로 계산할 때 차감하는 금액입니다.", ["source.nts.income-tax.rates"]),
    "term.eligibility-threshold": ("자격 기준금액", "지원금, 공제, 과세유형 판정에서 대상 여부를 가르는 소득·매출·재산·주택가액 등의 기준금액입니다.", ["source.nts.grant.2026-regular-press", "source.nts.vat.overview"]),
    "term.deadline": ("법정신고기한", "세법에 따라 과세표준신고서를 제출할 기한입니다.", ["source.national-tax-framework-act.2026.article2"]),
    "term.income-deduction": ("소득공제", "과세표준 계산 전에 소득금액에서 차감하는 공제입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit"]),
    "term.tax-credit": ("세액공제", "산출세액에서 직접 차감하는 공제입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.special-credit"]),
    "term.tax-reduction": ("세액감면", "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 조세지원입니다.", ["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"]),
    "term.deduction-limit": ("소득공제 종합한도", "과도한 소득공제 적용을 배제하기 위해 일정 소득공제 항목 합계에 적용되는 한도입니다.", ["source.nts.year-end-settlement.deduction-limit"]),
    "term.total-income": ("총소득", "근로·자녀장려금 자격 판정에서 근로, 사업, 종교인, 기타, 이자·배당·연금소득을 합산한 금액입니다.", ["source.nts.grant.eligibility"]),
    "term.gross-pay": ("총급여액 등", "장려금 지급액 결정과 홑벌이·맞벌이 구분 등에 쓰이는 근로, 사업, 종교인소득의 합계 기준입니다.", ["source.nts.grant.eligibility"]),
    "term.property-requirement": ("재산요건", "근로·자녀장려금에서 가구원 재산 합계액으로 판정하는 요건입니다.", ["source.nts.grant.eligibility"]),
    "term.median-income": ("기준 중위소득", "복지급여와 정책금융 지원대상 판정에 쓰이는 가구원 수별 중위소득 기준입니다.", ["source.govkr.basic-livelihood-benefit", "source.fsc.youth-future-savings"]),
    "term.policy-finance": ("정책금융", "정부, 금융위원회, 금융공공기관 등이 취약계층·청년·서민·실수요자의 금융 접근성과 자산형성을 지원하기 위해 운영하는 금융상품입니다.", ["source.fsc.youth-future-savings", "source.kinfa.illegal-private-finance-prevention-loan", "source.hf.didimdol-loan"]),
    "term.policy-loan": ("정책대출", "지원대상·한도·금리·보증요건을 정책적으로 정해 일반 금융 접근이 어려운 대상에게 제공하는 대출 또는 보증 상품입니다.", ["source.kinfa.hessal-loan-youth", "source.kinfa.hessal-119", "source.hf.didimdol-loan"]),
    "term.debt-adjustment": ("채무조정", "상환이 어려운 채무자의 이자율, 상환기간, 유예기간, 원금감면 등을 조정해 경제적 재기를 지원하는 제도입니다.", ["source.ccrs.long-term-delinquent-debt-adjustment"]),
    "term.general-vat-taxpayer": ("일반과세자", "부가가치세에서 일반 세율과 매입세액 공제 구조를 적용받는 과세사업자 유형입니다.", ["source.nts.vat.overview", "source.nts.vat.filing-duty"]),
    "term.simple-vat-taxpayer": ("간이과세자", "부가가치세에서 직전 1년 매출액이 10,400만원 미만인 개인사업자 유형입니다.", ["source.nts.vat.overview", "source.nts.vat.filing-duty", "source.nts.business-registration.application"]),
    "term.withholding-obligor": ("원천징수의무자", "원천징수 대상 소득 또는 수입금액을 지급하면서 세액을 징수·신고·납부해야 하는 개인이나 법인입니다.", ["source.nts.withholding.overview"]),
    "term.capital-gain": ("양도차익", "양도가액에서 취득가액과 필요경비 등을 차감해 산출하는 양도소득세 계산의 핵심 금액입니다.", ["source.nts.capital-gains.overview"]),
    "term.heir": ("상속인", "상속을 원인으로 재산을 물려받아 상속세 신고·납부 의무자가 될 수 있는 사람입니다.", ["source.nts.inheritance.overview"]),
    "term.donee": ("수증자", "증여로 재산을 이전받아 증여세 신고·납부 의무자가 될 수 있는 사람입니다.", ["source.nts.gift.deadline"]),
    "term.publicly-notified-price": ("공시가격", "종합부동산세 등 부동산 보유세에서 과세대상 유형별 공제금액과 과세표준 계산에 쓰이는 공적 가격 기준입니다.", ["source.nts.comprehensive-real-estate.overview"]),
    "term.deadline-special-rule": ("기한의 특례", "신고·납부 기한일이 공휴일, 토요일 또는 근로자의 날이면 그 다음 날을 기한으로 보는 규칙입니다.", ["source.nts.tax-calendar.2026", "source.nts.income-tax.deadline"]),
    "term.customs": ("관세", "수입물품에 부과되는 조세입니다.", ["source.customs-act.2026.article14"]),
}


DEADLINES = {
    "deadline.income-tax.2025-return": {
        "title": "2025년 귀속 종합소득세 확정신고",
        "description": "2025년 귀속 종합소득세 일반 신고·납부는 2026년 5월 1일부터 2026년 6월 1일까지입니다. 성실신고확인서 제출자는 2026년 6월 30일까지입니다.",
        "basis_year": 2025,
        "start_date": "2026-05-01",
        "end_date": "2026-06-01",
        "sources": ["source.nts.income-tax.deadline"],
    },
    "deadline.year-end-settlement": {
        "title": "근로소득 연말정산",
        "description": "계속 근로자는 다음연도 2월분 근로소득 지급 시, 중도 퇴직자는 퇴직하는 달의 근로소득 지급 시 연말정산을 실시합니다.",
        "basis_year": None,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.year-end-settlement.calculation"],
    },
    "deadline.withholding.monthly": {
        "title": "원천세 신고 납부",
        "description": "매월분 원천세는 다음 달 10일까지 신고·납부하는 반복 기한으로 관리합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.tax-calendar.2026"],
    },
    "deadline.vat.periodic": {
        "title": "부가가치세 신고 납부",
        "description": "일반과세자는 예정·확정 신고 구조를 따르며, 2026년 세무일정상 1기 예정신고 납부는 2026년 4월 27일, 2기 예정신고 납부는 2026년 10월 26일로 관리합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.vat.overview", "source.nts.vat.filing-duty", "source.nts.tax-calendar.2026"],
    },
    "deadline.vat.general.first-final": {
        "title": "부가가치세 일반과세자 1기 확정신고",
        "description": "일반과세자의 제1기 과세기간은 1월 1일부터 6월 30일까지이고, 확정신고·납부기한은 7월 1일부터 7월 25일까지입니다.",
        "basis_year": 2026,
        "start_date": "2026-07-01",
        "end_date": "2026-07-25",
        "sources": ["source.nts.vat.filing-duty"],
    },
    "deadline.vat.general.second-final": {
        "title": "부가가치세 일반과세자 2기 확정신고",
        "description": "일반과세자의 제2기 과세기간은 7월 1일부터 12월 31일까지이고, 확정신고·납부기한은 다음 해 1월 1일부터 1월 25일까지입니다.",
        "basis_year": 2026,
        "start_date": "2027-01-01",
        "end_date": "2027-01-25",
        "sources": ["source.nts.vat.filing-duty"],
    },
    "deadline.vat.simplified.annual": {
        "title": "부가가치세 간이과세자 연간 확정신고",
        "description": "간이과세자는 1월 1일부터 12월 31일까지를 과세기간으로 하며, 다음 해 1월 1일부터 1월 25일까지 확정신고·납부합니다.",
        "basis_year": 2026,
        "start_date": "2027-01-01",
        "end_date": "2027-01-25",
        "sources": ["source.nts.vat.filing-duty"],
    },
    "deadline.vat.simplified.preliminary": {
        "title": "부가가치세 간이과세자 예정신고 예외",
        "description": "직전연도 공급대가 4,800만원 이상 1억400만원 미만인 간이과세자가 예정부과기간에 세금계산서를 발급한 경우 7월 1일부터 7월 25일까지 예정신고합니다.",
        "basis_year": 2026,
        "start_date": "2026-07-01",
        "end_date": "2026-07-25",
        "sources": ["source.nts.vat.filing-duty"],
    },
    "deadline.withholding.semiannual": {
        "title": "원천세 반기별 납부",
        "description": "반기별 원천징수의무자는 원천징수한 소득세를 그 징수일이 속하는 반기의 마지막 달의 다음 달 10일까지 납부합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.business-income.withholding"],
    },
    "deadline.capital-gains.preliminary": {
        "title": "양도소득세 예정신고",
        "description": "토지·건물·부동산에 관한 권리·기타자산은 양도일이 속하는 달의 말일부터 2개월 이내, 주식·출자지분은 양도일이 속하는 반기의 말일부터 2개월 이내 예정신고합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.capital-gains.deadline"],
    },
    "deadline.capital-gains.final": {
        "title": "양도소득세 확정신고",
        "description": "양도소득세 확정신고는 양도한 연도의 다음연도 5월 1일부터 5월 31일까지입니다.",
        "basis_year": 2026,
        "start_date": "2027-05-01",
        "end_date": "2027-05-31",
        "sources": ["source.nts.capital-gains.deadline"],
    },
    "deadline.inheritance.resident": {
        "title": "상속세 거주자 신고납부",
        "description": "피상속인이 거주자인 경우 상속개시일이 속하는 달의 말일부터 6개월 이내에 상속세를 신고·납부합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.inheritance.overview"],
    },
    "deadline.inheritance.nonresident": {
        "title": "상속세 비거주자 신고납부",
        "description": "피상속인이나 상속인 전원이 비거주자인 경우 상속개시일이 속하는 달의 말일부터 9개월 이내에 상속세를 신고·납부합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.inheritance.overview"],
    },
    "deadline.gift.general": {
        "title": "증여세 일반 증여 신고납부",
        "description": "일반 증여는 재산을 증여받은 날이 속하는 달의 말일부터 3개월 이내에 증여세를 신고·납부합니다.",
        "basis_year": 2026,
        "start_date": None,
        "end_date": None,
        "sources": ["source.nts.gift.deadline"],
    },
    "deadline.grant.regular.2025-income": {
        "title": "2025년 귀속 근로·자녀장려금 정기신청",
        "description": "2025년 귀속 근로·자녀장려금 정기신청은 2026년 5월 신청 흐름으로 관리하고, 2026년에는 6월 1일까지로 기한의 특례를 반영합니다.",
        "basis_year": 2025,
        "start_date": "2026-05-01",
        "end_date": "2026-06-01",
        "sources": ["source.nts.grant.eligibility", "source.nts.grant.deadline"],
    },
    "deadline.grant.semiannual.2026": {
        "title": "2026년 근로장려금 반기신청분 지급",
        "description": "2026년 상반기분은 2026년 12월 30일, 하반기분은 2027년 6월 30일 지급기한으로 관리합니다.",
        "basis_year": 2026,
        "start_date": "2026-12-30",
        "end_date": "2027-06-30",
        "sources": ["source.nts.grant.deadline"],
    },
}


INCOME_TAX_RATE_CRITERIA = [
    {"label": "1,400만원 이하", "basis": "과세표준", "condition": "1,400만원 이하", "threshold_krw_max": 14_000_000, "rate_percent": 6, "progressive_deduction_krw": 0, "source": "source.nts.income-tax.rates"},
    {"label": "1,400만원 초과 5,000만원 이하", "basis": "과세표준", "condition": "1,400만원 초과 5,000만원 이하", "threshold_krw_min": 14_000_000, "threshold_krw_max": 50_000_000, "rate_percent": 15, "progressive_deduction_krw": 1_260_000, "source": "source.nts.income-tax.rates"},
    {"label": "5,000만원 초과 8,800만원 이하", "basis": "과세표준", "condition": "5,000만원 초과 8,800만원 이하", "threshold_krw_min": 50_000_000, "threshold_krw_max": 88_000_000, "rate_percent": 24, "progressive_deduction_krw": 5_760_000, "source": "source.nts.income-tax.rates"},
    {"label": "8,800만원 초과 1억5,000만원 이하", "basis": "과세표준", "condition": "8,800만원 초과 1억5,000만원 이하", "threshold_krw_min": 88_000_000, "threshold_krw_max": 150_000_000, "rate_percent": 35, "progressive_deduction_krw": 15_440_000, "source": "source.nts.income-tax.rates"},
    {"label": "1억5,000만원 초과 3억원 이하", "basis": "과세표준", "condition": "1억5,000만원 초과 3억원 이하", "threshold_krw_min": 150_000_000, "threshold_krw_max": 300_000_000, "rate_percent": 38, "progressive_deduction_krw": 19_940_000, "source": "source.nts.income-tax.rates"},
    {"label": "3억원 초과 5억원 이하", "basis": "과세표준", "condition": "3억원 초과 5억원 이하", "threshold_krw_min": 300_000_000, "threshold_krw_max": 500_000_000, "rate_percent": 40, "progressive_deduction_krw": 25_940_000, "source": "source.nts.income-tax.rates"},
    {"label": "5억원 초과 10억원 이하", "basis": "과세표준", "condition": "5억원 초과 10억원 이하", "threshold_krw_min": 500_000_000, "threshold_krw_max": 1_000_000_000, "rate_percent": 42, "progressive_deduction_krw": 35_940_000, "source": "source.nts.income-tax.rates"},
    {"label": "10억원 초과", "basis": "과세표준", "condition": "10억원 초과", "threshold_krw_min": 1_000_000_000, "rate_percent": 45, "progressive_deduction_krw": 65_940_000, "source": "source.nts.income-tax.rates"},
]


CORPORATE_TAX_RATE_CRITERIA = [
    {"label": "2억원 이하", "basis": "각 사업연도 소득 과세표준", "condition": "2억원 이하", "threshold_krw_max": 200_000_000, "rate_percent": 10, "progressive_deduction_krw": 0, "note": "2026.1.1. 이후 개시 사업연도 기준", "source": "source.nts.corporate-tax.rates"},
    {"label": "2억원 초과 200억원 이하", "basis": "각 사업연도 소득 과세표준", "condition": "2억원 초과 200억원 이하", "threshold_krw_min": 200_000_000, "threshold_krw_max": 20_000_000_000, "rate_percent": 20, "progressive_deduction_krw": 20_000_000, "note": "2026.1.1. 이후 개시 사업연도 기준", "source": "source.nts.corporate-tax.rates"},
    {"label": "200억원 초과 3,000억원 이하", "basis": "각 사업연도 소득 과세표준", "condition": "200억원 초과 3,000억원 이하", "threshold_krw_min": 20_000_000_000, "threshold_krw_max": 300_000_000_000, "rate_percent": 22, "progressive_deduction_krw": 420_000_000, "note": "2026.1.1. 이후 개시 사업연도 기준", "source": "source.nts.corporate-tax.rates"},
    {"label": "3,000억원 초과", "basis": "각 사업연도 소득 과세표준", "condition": "3,000억원 초과", "threshold_krw_min": 300_000_000_000, "rate_percent": 25, "progressive_deduction_krw": 9_420_000_000, "note": "2026.1.1. 이후 개시 사업연도 기준", "source": "source.nts.corporate-tax.rates"},
]


INHERITANCE_GIFT_RATE_CRITERIA = [
    {"label": "1억원 이하", "basis": "과세표준", "condition": "1억원 이하", "threshold_krw_max": 100_000_000, "rate_percent": 10, "progressive_deduction_krw": 0, "source": "source.nts.inheritance.rates"},
    {"label": "1억원 초과 5억원 이하", "basis": "과세표준", "condition": "1억원 초과 5억원 이하", "threshold_krw_min": 100_000_000, "threshold_krw_max": 500_000_000, "rate_percent": 20, "progressive_deduction_krw": 10_000_000, "source": "source.nts.inheritance.rates"},
    {"label": "5억원 초과 10억원 이하", "basis": "과세표준", "condition": "5억원 초과 10억원 이하", "threshold_krw_min": 500_000_000, "threshold_krw_max": 1_000_000_000, "rate_percent": 30, "progressive_deduction_krw": 60_000_000, "source": "source.nts.inheritance.rates"},
    {"label": "10억원 초과 30억원 이하", "basis": "과세표준", "condition": "10억원 초과 30억원 이하", "threshold_krw_min": 1_000_000_000, "threshold_krw_max": 3_000_000_000, "rate_percent": 40, "progressive_deduction_krw": 160_000_000, "source": "source.nts.inheritance.rates"},
    {"label": "30억원 초과", "basis": "과세표준", "condition": "30억원 초과", "threshold_krw_min": 3_000_000_000, "rate_percent": 50, "progressive_deduction_krw": 460_000_000, "source": "source.nts.inheritance.rates"},
]

GIFT_RATE_CRITERIA = [{**criterion, "source": "source.nts.gift.rates"} for criterion in INHERITANCE_GIFT_RATE_CRITERIA]


VAT_CRITERIA = [
    {"label": "일반과세자 매출 기준", "basis": "1년 매출액", "condition": "1억400만원 이상", "threshold_krw_min": 104_000_000, "benefit": "일반과세자", "source": "source.nts.vat.overview"},
    {"label": "간이과세자 매출 기준", "basis": "1년 매출액", "condition": "1억400만원 미만", "threshold_krw_max": 104_000_000, "benefit": "간이과세자", "source": "source.nts.vat.overview"},
    {"label": "일반과세자 세율", "basis": "매출세액", "condition": "매출액에 기본세율 적용", "rate_percent": 10, "note": "영세율 적용 대상은 0%", "source": "source.nts.vat.filing-duty"},
    {"label": "간이과세자 업종별 부가가치율", "basis": "업종별 부가가치율", "condition": "2021.7.1. 이후 업종별 15%~40%", "rate_percent_min": 15, "rate_percent_max": 40, "note": "납부세액은 매출액 × 업종별 부가가치율 × 10% - 공제세액", "source": "source.nts.vat.overview"},
    {"label": "간이과세자 예정신고 대상", "basis": "직전연도 공급대가", "condition": "4,800만원 이상 1억400만원 미만이고 예정부과기간에 세금계산서 발급", "threshold_krw_min": 48_000_000, "threshold_krw_max": 104_000_000, "source": "source.nts.vat.filing-duty"},
    {"label": "간이과세자 납부의무 면제", "basis": "직전연도 공급대가", "condition": "4,800만원 미만", "threshold_krw_max": 48_000_000, "benefit": "납부세액 납부의무 면제 가능", "source": "source.nts.vat.filing-duty"},
]


BUSINESS_INCOME_WITHHOLDING_CRITERIA = [
    {"label": "사업소득 원천징수세율", "basis": "원천징수 대상 사업소득 지급금액", "condition": "사업소득 지급 시", "rate_percent": 3, "note": "지방소득세는 별도 확인", "source": "source.nts.business-income.withholding"},
]


CRE_CRITERIA = [
    {"label": "주택 공제금액", "basis": "공시가격 합계액", "condition": "주택", "deduction_krw": 900_000_000, "note": "1세대 1주택자는 12억원", "source": "source.nts.comprehensive-real-estate.overview"},
    {"label": "1세대 1주택자 주택 공제금액", "basis": "공시가격 합계액", "condition": "1세대 1주택자", "deduction_krw": 1_200_000_000, "source": "source.nts.comprehensive-real-estate.overview"},
    {"label": "종합합산토지 공제금액", "basis": "공시가격 합계액", "condition": "종합합산토지", "deduction_krw": 500_000_000, "source": "source.nts.comprehensive-real-estate.overview"},
    {"label": "별도합산토지 공제금액", "basis": "공시가격 합계액", "condition": "별도합산토지", "deduction_krw": 8_000_000_000, "source": "source.nts.comprehensive-real-estate.overview"},
    {"label": "주택 2주택 이하 3억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 3억원 이하", "threshold_krw_max": 300_000_000, "rate_percent": 0.5, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 6억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 6억원 이하", "threshold_krw_max": 600_000_000, "rate_percent": 0.7, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 12억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 12억원 이하", "threshold_krw_max": 1_200_000_000, "rate_percent": 1.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 25억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 25억원 이하", "threshold_krw_max": 2_500_000_000, "rate_percent": 1.3, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 50억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 50억원 이하", "threshold_krw_max": 5_000_000_000, "rate_percent": 1.5, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 94억원 이하", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 94억원 이하", "threshold_krw_max": 9_400_000_000, "rate_percent": 2.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 2주택 이하 94억원 초과", "basis": "종부세 과세표준", "condition": "주택 2주택 이하, 94억원 초과", "threshold_krw_min": 9_400_000_000, "rate_percent": 2.7, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 3주택 이상 25억원 이하", "basis": "종부세 과세표준", "condition": "주택 3주택 이상, 25억원 이하", "threshold_krw_max": 2_500_000_000, "rate_percent": 2.0, "note": "3억원 이하 0.5%, 6억원 이하 0.7%, 12억원 이하 1.0%", "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 3주택 이상 50억원 이하", "basis": "종부세 과세표준", "condition": "주택 3주택 이상, 50억원 이하", "threshold_krw_max": 5_000_000_000, "rate_percent": 3.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 3주택 이상 94억원 이하", "basis": "종부세 과세표준", "condition": "주택 3주택 이상, 94억원 이하", "threshold_krw_max": 9_400_000_000, "rate_percent": 4.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "주택 3주택 이상 94억원 초과", "basis": "종부세 과세표준", "condition": "주택 3주택 이상, 94억원 초과", "threshold_krw_min": 9_400_000_000, "rate_percent": 5.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "종합합산토지 15억원 이하", "basis": "종부세 과세표준", "condition": "종합합산토지 15억원 이하", "threshold_krw_max": 1_500_000_000, "rate_percent": 1.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "종합합산토지 45억원 이하", "basis": "종부세 과세표준", "condition": "종합합산토지 45억원 이하", "threshold_krw_max": 4_500_000_000, "rate_percent": 2.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "종합합산토지 45억원 초과", "basis": "종부세 과세표준", "condition": "종합합산토지 45억원 초과", "threshold_krw_min": 4_500_000_000, "rate_percent": 3.0, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "별도합산토지 200억원 이하", "basis": "종부세 과세표준", "condition": "별도합산토지 200억원 이하", "threshold_krw_max": 20_000_000_000, "rate_percent": 0.5, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "별도합산토지 400억원 이하", "basis": "종부세 과세표준", "condition": "별도합산토지 400억원 이하", "threshold_krw_max": 40_000_000_000, "rate_percent": 0.6, "source": "source.nts.comprehensive-real-estate.rates"},
    {"label": "별도합산토지 400억원 초과", "basis": "종부세 과세표준", "condition": "별도합산토지 400억원 초과", "threshold_krw_min": 40_000_000_000, "rate_percent": 0.7, "source": "source.nts.comprehensive-real-estate.rates"},
]


LOCAL_PROPERTY_TAX_CRITERIA = [
    {"label": "주택 6천만원 이하", "basis": "재산세 과세표준", "condition": "주택 6천만원 이하", "threshold_krw_max": 60_000_000, "rate_percent": 0.1, "progressive_deduction_krw": 0, "source": "source.nts.real-estate-tax.faq"},
    {"label": "주택 1억5천만원 이하", "basis": "재산세 과세표준", "condition": "주택 1억5천만원 이하", "threshold_krw_max": 150_000_000, "rate_percent": 0.15, "progressive_deduction_krw": 30_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "주택 3억원 이하", "basis": "재산세 과세표준", "condition": "주택 3억원 이하", "threshold_krw_max": 300_000_000, "rate_percent": 0.25, "progressive_deduction_krw": 180_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "주택 3억원 초과", "basis": "재산세 과세표준", "condition": "주택 3억원 초과", "threshold_krw_min": 300_000_000, "rate_percent": 0.4, "progressive_deduction_krw": 630_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "종합합산 5천만원 이하", "basis": "재산세 과세표준", "condition": "종합합산 5천만원 이하", "threshold_krw_max": 50_000_000, "rate_percent": 0.2, "progressive_deduction_krw": 0, "source": "source.nts.real-estate-tax.faq"},
    {"label": "종합합산 1억원 이하", "basis": "재산세 과세표준", "condition": "종합합산 1억원 이하", "threshold_krw_max": 100_000_000, "rate_percent": 0.3, "progressive_deduction_krw": 50_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "종합합산 1억원 초과", "basis": "재산세 과세표준", "condition": "종합합산 1억원 초과", "threshold_krw_min": 100_000_000, "rate_percent": 0.5, "progressive_deduction_krw": 250_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "별도합산 2억원 이하", "basis": "재산세 과세표준", "condition": "별도합산 2억원 이하", "threshold_krw_max": 200_000_000, "rate_percent": 0.2, "progressive_deduction_krw": 0, "source": "source.nts.real-estate-tax.faq"},
    {"label": "별도합산 10억원 이하", "basis": "재산세 과세표준", "condition": "별도합산 10억원 이하", "threshold_krw_max": 1_000_000_000, "rate_percent": 0.3, "progressive_deduction_krw": 200_000, "source": "source.nts.real-estate-tax.faq"},
    {"label": "별도합산 10억원 초과", "basis": "재산세 과세표준", "condition": "별도합산 10억원 초과", "threshold_krw_min": 1_000_000_000, "rate_percent": 0.4, "progressive_deduction_krw": 1_200_000, "source": "source.nts.real-estate-tax.faq"},
]


EITC_CRITERIA = [
    {"label": "단독가구 총소득", "basis": "부부합산 총소득", "condition": "2,200만원 미만", "threshold_krw_max": 22_000_000, "max_amount_krw": 1_650_000, "source": "source.nts.eitc.intro"},
    {"label": "홑벌이가구 총소득", "basis": "부부합산 총소득", "condition": "3,200만원 미만", "threshold_krw_max": 32_000_000, "max_amount_krw": 2_850_000, "source": "source.nts.eitc.intro"},
    {"label": "맞벌이가구 총소득", "basis": "부부합산 총소득", "condition": "4,400만원 미만", "threshold_krw_max": 44_000_000, "max_amount_krw": 3_300_000, "source": "source.nts.eitc.intro"},
    {"label": "재산요건", "basis": "가구원 전체 재산 합계액", "condition": "2억4천만원 미만", "threshold_krw_max": 240_000_000, "benefit": "신청 가능", "source": "source.nts.grant.2026-regular-press"},
    {"label": "재산 감액구간", "basis": "가구원 전체 재산 합계액", "condition": "1억7천만원 이상 2억4천만원 미만", "threshold_krw_min": 170_000_000, "threshold_krw_max": 240_000_000, "benefit": "산정액의 50% 지급", "source": "source.nts.grant.2026-regular-press"},
]


CTC_CRITERIA = [
    {"label": "홑벌이·맞벌이 총소득", "basis": "부부합산 총소득", "condition": "7,000만원 미만", "threshold_krw_max": 70_000_000, "max_amount_krw": 1_000_000, "note": "자녀 1인당 최대 100만원, 최소 50만원", "source": "source.nts.ctc.intro"},
    {"label": "부양자녀", "basis": "자녀 연령", "condition": "18세 미만 부양자녀", "benefit": "자녀장려금 대상", "source": "source.nts.ctc.intro"},
    {"label": "재산요건", "basis": "가구원 전체 재산 합계액", "condition": "2억4천만원 미만", "threshold_krw_max": 240_000_000, "benefit": "신청 가능", "source": "source.nts.grant.2026-regular-press"},
    {"label": "재산 감액구간", "basis": "가구원 전체 재산 합계액", "condition": "1억7천만원 이상 2억4천만원 미만", "threshold_krw_min": 170_000_000, "threshold_krw_max": 240_000_000, "benefit": "산정액의 50% 지급", "source": "source.nts.grant.2026-regular-press"},
]


YOUTH_LEAP_CRITERIA = [
    {"label": "나이", "basis": "계좌개설일 기준 만 나이", "condition": "19세 이상 34세 이하", "note": "병역이행기간은 최대 6년까지 차감", "source": "source.kinfa.youth-leap"},
    {"label": "개인소득 총급여", "basis": "직전 과세기간 총급여액", "condition": "7,500만원 이하", "threshold_krw_max": 75_000_000, "source": "source.kinfa.youth-leap"},
    {"label": "개인소득 종합소득", "basis": "종합소득과세표준에 합산되는 종합소득금액", "condition": "6,300만원 이하", "threshold_krw_max": 63_000_000, "source": "source.kinfa.youth-leap"},
    {"label": "가구소득", "basis": "가구원 수별 기준 중위소득", "condition": "250% 이하", "benefit": "가입 대상", "source": "source.kinfa.youth-leap"},
    {"label": "금융소득종합과세 제외", "basis": "직전 3개 과세기간", "condition": "금융소득종합과세 대상 이력 없음", "benefit": "가입 가능", "source": "source.kinfa.youth-leap"},
]


MONTHLY_RENT_CREDIT_CRITERIA = [
    {"label": "공제대상자 소득", "basis": "총급여", "condition": "8,000만원 이하", "threshold_krw_max": 80_000_000, "source": "source.nts.monthly-rent-credit"},
    {"label": "공제대상자 종합소득", "basis": "종합소득금액", "condition": "7,000만원 이하", "threshold_krw_max": 70_000_000, "source": "source.nts.monthly-rent-credit"},
    {"label": "17% 공제율", "basis": "총급여", "condition": "5,500만원 이하", "threshold_krw_max": 55_000_000, "rate_percent": 17, "limit_krw": 10_000_000, "source": "source.nts.monthly-rent-credit"},
    {"label": "15% 공제율", "basis": "총급여", "condition": "5,500만원 초과 8,000만원 이하", "threshold_krw_min": 55_000_000, "threshold_krw_max": 80_000_000, "rate_percent": 15, "limit_krw": 10_000_000, "source": "source.nts.monthly-rent-credit"},
    {"label": "공제대상 주택", "basis": "주택 규모·기준시가", "condition": "국민주택규모 또는 기준시가 4억원 이하", "threshold_krw_max": 400_000_000, "source": "source.nts.monthly-rent-credit"},
]


CREDIT_CARD_DEDUCTION_CRITERIA = [
    {"label": "사용금액 문턱", "basis": "신용카드 등 사용금액", "condition": "총급여액의 25% 초과분", "rate_percent": 25, "note": "공제 대상 사용금액 산정 기준", "source": "source.nts.credit-card-deduction"},
    {"label": "신용카드 공제율", "basis": "신용카드 사용금액", "condition": "총급여 25% 초과분 중 신용카드", "rate_percent": 15, "source": "source.nts.credit-card-deduction"},
    {"label": "현금영수증·직불카드 공제율", "basis": "현금영수증·직불카드 등", "condition": "총급여 25% 초과분 중 현금영수증·직불카드", "rate_percent": 30, "source": "source.nts.credit-card-deduction"},
    {"label": "전통시장·대중교통 공제율", "basis": "전통시장·대중교통 사용금액", "condition": "총급여 25% 초과분 중 전통시장·대중교통", "rate_percent": 40, "source": "source.nts.credit-card-deduction"},
]


PENSION_ACCOUNT_CREDIT_CRITERIA = [
    {"label": "총급여 5,500만원 이하", "basis": "총급여 또는 종합소득금액", "condition": "총급여 5,500만원 이하 또는 종합소득금액 4,500만원 이하", "threshold_krw_max": 55_000_000, "limit_krw": 9_000_000, "rate_percent": 15, "note": "연금저축 600만원, 퇴직연금 포함 900만원 한도", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "총급여 5,500만원 초과", "basis": "총급여 또는 종합소득금액", "condition": "총급여 5,500만원 초과", "threshold_krw_min": 55_000_000, "limit_krw": 9_000_000, "rate_percent": 12, "note": "연금저축 600만원, 퇴직연금 포함 900만원 한도", "source": "source.nts.year-end-settlement.calculation"},
]


MEDICAL_EXPENSE_CREDIT_CRITERIA = [
    {"label": "의료비 공제 문턱", "basis": "의료비 지출액", "condition": "총급여액의 3% 초과분", "rate_percent": 3, "note": "초과분이 공제대상 의료비", "source": "source.nts.year-end-settlement.special-credit"},
    {"label": "일반 의료비", "basis": "일반 기본공제대상자 의료비", "condition": "연 700만원 한도", "limit_krw": 7_000_000, "rate_percent": 15, "source": "source.nts.year-end-settlement.special-credit"},
    {"label": "본인·6세 이하·65세 이상·장애인 의료비", "basis": "해당 의료비", "condition": "한도 없음", "rate_percent": 15, "source": "source.nts.year-end-settlement.special-credit"},
    {"label": "난임시술비", "basis": "난임시술비", "condition": "한도 없음", "rate_percent": 30, "source": "source.nts.year-end-settlement.special-credit"},
]


PERSONAL_BASIC_DEDUCTION_CRITERIA = [
    {"label": "기본공제 대상자 1명당", "basis": "본인·배우자·부양가족", "condition": "기본공제 대상자", "deduction_krw": 1_500_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "부양가족 소득요건", "basis": "연간 소득금액", "condition": "100만원 이하", "threshold_krw_max": 1_000_000, "note": "근로소득만 있는 경우 총급여 500만원 이하", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "근로소득만 있는 부양가족", "basis": "총급여", "condition": "500만원 이하", "threshold_krw_max": 5_000_000, "source": "source.nts.year-end-settlement.calculation"},
]


PERSONAL_ADDITIONAL_DEDUCTION_CRITERIA = [
    {"label": "경로우대", "basis": "기본공제대상자", "condition": "70세 이상", "deduction_krw": 1_000_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "장애인", "basis": "기본공제대상자", "condition": "장애인", "deduction_krw": 2_000_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "부녀자", "basis": "종합소득금액", "condition": "3,000만원 이하 등 요건 충족", "threshold_krw_max": 30_000_000, "deduction_krw": 500_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "한부모", "basis": "배우자가 없는 기본공제대상자", "condition": "기본공제대상 직계비속 또는 입양자 있음", "deduction_krw": 1_000_000, "note": "부녀자공제와 중복 시 한부모공제 적용", "source": "source.nts.year-end-settlement.calculation"},
]


PERSONAL_DEDUCTION_CRITERIA = PERSONAL_BASIC_DEDUCTION_CRITERIA + PERSONAL_ADDITIONAL_DEDUCTION_CRITERIA


PENSION_INSURANCE_DEDUCTION_CRITERIA = [
    {"label": "공적연금 근로자 부담금", "basis": "국민연금 등 공적연금보험료", "condition": "근로자가 부담한 공적연금보험료", "benefit": "전액 소득공제", "source": "source.nts.year-end-settlement.calculation"},
]


HEALTH_INSURANCE_PREMIUM_DEDUCTION_CRITERIA = [
    {"label": "국민건강보험·노인장기요양보험", "basis": "본인 부담 보험료", "condition": "근로제공기간 중 부담분", "benefit": "전액 소득공제", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "고용보험", "basis": "본인 부담 보험료", "condition": "근로제공기간 중 부담분", "benefit": "전액 소득공제", "source": "source.nts.year-end-settlement.calculation"},
]


HOUSING_FUNDS_DEDUCTION_CRITERIA = [
    {"label": "주택임차차입금 원리금", "basis": "원리금 상환액", "condition": "무주택 세대주 등, 국민주택규모 주택 임차", "rate_percent": 40, "limit_krw": 4_000_000, "note": "주택마련저축 공제금액과 합산 연 400만원 한도", "source": "source.nts.housing-rent-principal-deduction"},
    {"label": "장기주택저당차입금 10년 이상", "basis": "이자상환액", "condition": "상환기간 10년 이상, 고정금리 또는 비거치식 분할상환", "limit_krw": 6_000_000, "source": "source.nts.housing-mortgage-interest-deduction"},
    {"label": "장기주택저당차입금 15년 이상", "basis": "이자상환액", "condition": "상환기간 15년 이상", "limit_krw": 8_000_000, "source": "source.nts.housing-mortgage-interest-deduction"},
    {"label": "장기주택저당차입금 15년 이상 우대", "basis": "이자상환액", "condition": "상환기간 15년 이상, 고정금리 또는 비거치식 분할상환", "limit_krw": 18_000_000, "source": "source.nts.housing-mortgage-interest-deduction"},
    {"label": "장기주택저당차입금 15년 이상 최우대", "basis": "이자상환액", "condition": "상환기간 15년 이상, 고정금리이고 비거치식 분할상환", "limit_krw": 20_000_000, "source": "source.nts.housing-mortgage-interest-deduction"},
]


SPECIAL_INCOME_DEDUCTION_CRITERIA = HEALTH_INSURANCE_PREMIUM_DEDUCTION_CRITERIA + HOUSING_FUNDS_DEDUCTION_CRITERIA


OTHER_INCOME_DEDUCTION_CRITERIA = [
    {"label": "소득공제 종합한도", "basis": "종합한도 적용 소득공제 합계", "condition": "2,500만원 초과액은 과세표준에 합산", "limit_krw": 25_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "주택자금·주택마련저축", "basis": "주택자금공제와 주택마련저축", "condition": "종합한도 적용 대상", "benefit": "종합한도 내 소득공제", "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "투자·우리사주·장기저축", "basis": "중소기업창업투자조합 출자 등, 우리사주조합 출연금, 장기집합투자증권저축", "condition": "일부 벤처투자 예외를 제외하고 종합한도 적용 대상", "benefit": "종합한도 내 소득공제", "source": "source.nts.year-end-settlement.deduction-limit"},
]


PERSONAL_PENSION_SAVINGS_DEDUCTION_CRITERIA = [
    {"label": "개인연금저축 납입액", "basis": "2000.12.31. 이전 가입 개인연금저축", "condition": "연 납입액의 40%", "rate_percent": 40, "limit_krw": 720_000, "note": "연 180만원 납입 기준 최대 72만원 소득공제", "source": "source.nts.year-end-settlement.calculation"},
]


SMALL_BUSINESS_MUTUAL_AID_DEDUCTION_CRITERIA = [
    {"label": "근로소득금액 4천만원 이하", "basis": "근로소득금액", "condition": "4,000만원 이하", "threshold_krw_max": 40_000_000, "limit_krw": 5_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "근로소득금액 4천만원 초과 1억원 이하", "basis": "근로소득금액", "condition": "4,000만원 초과 1억원 이하", "threshold_krw_min": 40_000_000, "threshold_krw_max": 100_000_000, "limit_krw": 3_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "근로소득금액 1억원 초과", "basis": "근로소득금액", "condition": "1억원 초과", "threshold_krw_min": 100_000_000, "limit_krw": 2_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
]


HOUSING_SAVINGS_DEDUCTION_CRITERIA = [
    {"label": "총급여 요건", "basis": "총급여액", "condition": "7,000만원 이하", "threshold_krw_max": 70_000_000, "source": "source.nts.housing-savings-deduction"},
    {"label": "납입액 공제", "basis": "주택마련저축 납입액", "condition": "연 납입액 300만원 한도", "threshold_krw_max": 3_000_000, "rate_percent": 40, "limit_krw": 1_200_000, "source": "source.nts.housing-savings-deduction"},
]


INVESTMENT_ASSOCIATION_DEDUCTION_CRITERIA = [
    {"label": "일반 투자조합 출자", "basis": "출자 또는 투자금액", "condition": "중소기업창업투자조합 등", "rate_percent": 10, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "벤처기업 등 3천만원 이하", "basis": "출자 또는 투자금액", "condition": "벤처기업 등 직접·간접 투자 3천만원 이하", "threshold_krw_max": 30_000_000, "rate_percent": 100, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "벤처기업 등 3천만원 초과 5천만원 이하", "basis": "출자 또는 투자금액", "condition": "3천만원 초과 5천만원 이하", "threshold_krw_min": 30_000_000, "threshold_krw_max": 50_000_000, "rate_percent": 70, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "벤처기업 등 5천만원 초과", "basis": "출자 또는 투자금액", "condition": "5천만원 초과", "threshold_krw_min": 50_000_000, "rate_percent": 30, "source": "source.nts.year-end-settlement.deduction-limit"},
]


EMPLOYEE_STOCK_OWNERSHIP_DEDUCTION_CRITERIA = [
    {"label": "일반 우리사주조합 출연금", "basis": "우리사주조합 출연금", "condition": "조합원 출연금", "limit_krw": 4_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
    {"label": "벤처기업 우리사주조합 출연금", "basis": "우리사주조합 출연금", "condition": "벤처기업 조합원 출연금", "limit_krw": 15_000_000, "source": "source.nts.year-end-settlement.deduction-limit"},
]


EMPLOYMENT_MAINTENANCE_WORKER_DEDUCTION_CRITERIA = [
    {"label": "임금삭감액 공제", "basis": "고용유지 중소기업 근로자 임금삭감액", "condition": "고용유지 요건 충족", "rate_percent": 50, "limit_krw": 10_000_000, "source": "source.nts.year-end-settlement.calculation"},
]


LONG_TERM_FUND_DEDUCTION_CRITERIA = [
    {"label": "장기집합투자증권저축 납입액", "basis": "연 납입액", "condition": "연 600만원 한도", "threshold_krw_max": 6_000_000, "rate_percent": 40, "limit_krw": 2_400_000, "source": "source.nts.year-end-settlement.deduction-limit"},
]


YOUTH_LONG_TERM_FUND_DEDUCTION_CRITERIA = [
    {"label": "가입 소득요건", "basis": "총급여 또는 종합소득금액", "condition": "총급여 5,000만원 이하 또는 종합소득금액 3,800만원 이하", "threshold_krw_max": 50_000_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "청년형 장기집합투자증권저축 납입액", "basis": "연 납입액", "condition": "연 600만원 한도", "threshold_krw_max": 6_000_000, "rate_percent": 40, "limit_krw": 2_400_000, "source": "source.nts.year-end-settlement.calculation"},
]


EARNED_INCOME_TAX_CREDIT_CRITERIA = [
    {"label": "산출세액 130만원 이하", "basis": "근로소득 산출세액", "condition": "130만원 이하", "threshold_krw_max": 1_300_000, "rate_percent": 55, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "산출세액 130만원 초과", "basis": "근로소득 산출세액", "condition": "130만원 초과", "threshold_krw_min": 1_300_000, "deduction_krw": 715_000, "rate_percent": 30, "note": "715,000원 + 130만원 초과금액의 30%", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "총급여 3,300만원 이하 한도", "basis": "총급여", "condition": "3,300만원 이하", "threshold_krw_max": 33_000_000, "limit_krw": 740_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "총급여 3,300만원 초과 7,000만원 이하 한도", "basis": "총급여", "condition": "3,300만원 초과 7,000만원 이하", "threshold_krw_min": 33_000_000, "threshold_krw_max": 70_000_000, "limit_krw": 660_000, "note": "74만원-[(총급여액-3,300만원)×0.8%], 최소 66만원", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "총급여 7,000만원 초과 1.2억원 이하 한도", "basis": "총급여", "condition": "7,000만원 초과 1.2억원 이하", "threshold_krw_min": 70_000_000, "threshold_krw_max": 120_000_000, "limit_krw": 500_000, "note": "66만원-[(총급여액-7,000만원)×1/2], 최소 50만원", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "총급여 1.2억원 초과 한도", "basis": "총급여", "condition": "1.2억원 초과", "threshold_krw_min": 120_000_000, "limit_krw": 200_000, "note": "50만원-[(총급여액-1.2억원)×1/2], 최소 20만원", "source": "source.nts.year-end-settlement.calculation"},
]


CHILD_TAX_CREDIT_CRITERIA = [
    {"label": "자녀 1명", "basis": "8세 이상 기본공제대상 자녀·손자녀", "condition": "1명", "deduction_krw": 250_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "자녀 2명", "basis": "8세 이상 기본공제대상 자녀·손자녀", "condition": "2명", "deduction_krw": 550_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "자녀 3명 이상", "basis": "8세 이상 기본공제대상 자녀·손자녀", "condition": "3명 이상", "deduction_krw": 550_000, "note": "2명을 초과하는 1명당 40만원 추가", "source": "source.nts.year-end-settlement.calculation"},
    {"label": "출산·입양 첫째", "basis": "출산·입양 신고 자녀", "condition": "첫째", "deduction_krw": 300_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "출산·입양 둘째", "basis": "출산·입양 신고 자녀", "condition": "둘째", "deduction_krw": 500_000, "source": "source.nts.year-end-settlement.calculation"},
    {"label": "출산·입양 셋째 이상", "basis": "출산·입양 신고 자녀", "condition": "셋째 이상", "deduction_krw": 700_000, "source": "source.nts.year-end-settlement.calculation"},
]


INSURANCE_PREMIUM_CREDIT_CRITERIA = [
    {"label": "보장성보험료", "basis": "생명보험·상해보험 등 보장성보험료", "condition": "기본공제대상자를 위해 지급", "limit_krw": 1_000_000, "rate_percent": 12, "source": "source.nts.year-end-settlement.special-credit"},
    {"label": "장애인전용 보장성보험료", "basis": "장애인을 피보험자 또는 수익자로 하는 장애인전용 보장성보험료", "condition": "장애인전용 보장성보험", "limit_krw": 1_000_000, "rate_percent": 15, "source": "source.nts.year-end-settlement.special-credit"},
]


EDUCATION_EXPENSE_CREDIT_CRITERIA = [
    {"label": "본인 교육비", "basis": "근로자 본인 교육비", "condition": "한도 없음", "rate_percent": 15, "source": "source.nts.education-expense-credit"},
    {"label": "취학전·초중고 교육비", "basis": "부양가족 1명당 교육비", "condition": "취학전 아동, 초·중·고등학생", "limit_krw": 3_000_000, "rate_percent": 15, "source": "source.nts.education-expense-credit"},
    {"label": "대학생 교육비", "basis": "부양가족 1명당 교육비", "condition": "대학생", "limit_krw": 9_000_000, "rate_percent": 15, "source": "source.nts.education-expense-credit"},
    {"label": "장애인 특수교육비", "basis": "장애인 특수교육비", "condition": "직계존속 포함, 소득제한 없음", "rate_percent": 15, "note": "한도 없음", "source": "source.nts.education-expense-credit"},
]


DONATION_CREDIT_CRITERIA = [
    {"label": "정치자금 10만원 이하", "basis": "정치자금기부금", "condition": "10만원 이하", "threshold_krw_max": 100_000, "rate_percent": 90.91, "rate_label": "세액공제율", "note": "100/110 세액공제", "source": "source.nts.donation-credit"},
    {"label": "정치자금 10만원 초과", "basis": "정치자금기부금", "condition": "10만원 초과", "threshold_krw_min": 100_000, "rate_percent": 15, "source": "source.nts.donation-credit"},
    {"label": "정치자금 3천만원 초과", "basis": "정치자금기부금", "condition": "3천만원 초과분", "threshold_krw_min": 30_000_000, "rate_percent": 25, "source": "source.nts.donation-credit"},
    {"label": "고향사랑 10만원 이하", "basis": "고향사랑기부금", "condition": "10만원 이하", "threshold_krw_max": 100_000, "rate_percent": 90.91, "rate_label": "세액공제율", "note": "100/110 세액공제", "source": "source.nts.donation-credit"},
    {"label": "특례·우리사주·일반 1천만원 이하", "basis": "공제한도 내 기부금", "condition": "1천만원 이하", "threshold_krw_max": 10_000_000, "rate_percent": 15, "source": "source.nts.donation-credit"},
    {"label": "특례·우리사주·일반 1천만원 초과", "basis": "공제한도 내 기부금", "condition": "1천만원 초과", "threshold_krw_min": 10_000_000, "rate_percent": 30, "source": "source.nts.donation-credit"},
]


SPECIAL_TAX_CREDIT_CRITERIA = INSURANCE_PREMIUM_CREDIT_CRITERIA + MEDICAL_EXPENSE_CREDIT_CRITERIA + EDUCATION_EXPENSE_CREDIT_CRITERIA + DONATION_CREDIT_CRITERIA[:2]


FOREIGN_TAX_PAID_CREDIT_CRITERIA = [
    {"label": "외국납부세액공제 한도", "basis": "국외원천소득 관련 외국납부세액", "condition": "국내 산출세액 중 국외원천소득 비율 상당액 한도", "benefit": "외국납부세액과 한도액 중 작은 금액 공제", "source": "source.nts.corporate-tax.reliefs"},
]


RND_CREDIT_CRITERIA = [
    {"label": "일반 연구·인력개발비", "basis": "연구·인력개발비", "condition": "기업규모·증가분 방식별 공제율 적용", "benefit": "일반 R&D 세액공제", "source": "source.nts.corporate-tax.reliefs"},
    {"label": "신성장·원천기술", "basis": "신성장·원천기술 연구개발비", "condition": "해당 기술 연구개발비", "benefit": "우대 공제율 적용", "source": "source.nts.corporate-tax.reliefs"},
    {"label": "국가전략기술", "basis": "국가전략기술 연구개발비", "condition": "반도체 등 국가전략기술 연구개발비", "benefit": "최고 우대 공제율 적용", "source": "source.nts.corporate-tax.reliefs"},
]


INTEGRATED_EMPLOYMENT_CREDIT_CRITERIA = [
    {"label": "고용 증가 인원", "basis": "상시근로자 증가 인원", "condition": "전년 대비 고용 증가", "benefit": "1인당 정액 세액공제", "source": "source.nts.corporate-tax.reliefs"},
    {"label": "우대 대상 고용", "basis": "청년·장애인·경력단절자 등", "condition": "정책대상 근로자 고용 증가", "benefit": "일반 상시근로자보다 우대 공제액 적용", "source": "source.nts.corporate-tax.reliefs"},
]


SME_EMPLOYMENT_INCOME_REDUCTION_CRITERIA = [
    {"label": "청년", "basis": "중소기업 취업자 근로소득세", "condition": "근로계약 체결일 현재 15~34세 이하", "rate_percent": 90, "rate_label": "감면율", "limit_krw": 2_000_000, "note": "감면기간 5년", "source": "source.nts.sme-employment-income-reduction"},
    {"label": "고령자", "basis": "중소기업 취업자 근로소득세", "condition": "근로계약 체결일 현재 60세 이상", "rate_percent": 70, "rate_label": "감면율", "limit_krw": 2_000_000, "note": "감면기간 3년", "source": "source.nts.sme-employment-income-reduction"},
    {"label": "장애인·경력단절근로자", "basis": "중소기업 취업자 근로소득세", "condition": "장애인 또는 경력단절근로자 요건 충족", "rate_percent": 70, "rate_label": "감면율", "limit_krw": 2_000_000, "note": "감면기간 3년", "source": "source.nts.sme-employment-income-reduction"},
]


STARTUP_SME_REDUCTION_CRITERIA = [
    {"label": "2026년 이후 일반 창업중소기업", "basis": "법인세 또는 소득세", "condition": "수도권 외 지역 또는 수도권 인구감소지역", "rate_percent": 50, "rate_label": "감면율", "note": "최초 소득발생 과세연도와 이후 4년", "source": "source.nts.corporate-tax-consulting.2026"},
    {"label": "2026년 이후 청년·생계형 창업", "basis": "법인세 또는 소득세", "condition": "수도권 외 지역 또는 수도권과밀억제권역 외", "rate_percent": 100, "rate_label": "감면율", "note": "수도권 과밀억제권역 50%, 수도권 75% 등 지역별 차등", "source": "source.nts.corporate-tax-consulting.2026"},
    {"label": "상시근로자 증가 추가감면", "basis": "상시근로자 증가율", "condition": "고용 증가 요건 충족", "rate_percent": 100, "rate_label": "추가감면 산식", "note": "상시근로자 증가율 × 100%", "source": "source.nts.corporate-tax-consulting.2026"},
]


SME_SPECIAL_REDUCTION_CRITERIA = [
    {"label": "소기업 수도권 제조업 등", "basis": "중소기업 특별세액감면", "condition": "소기업, 수도권 내 제조업·출판업 등", "rate_percent": 20, "rate_label": "감면율", "source": "source.nts.corporate-tax-consulting.2026"},
    {"label": "소기업 수도권 외 제조업 등", "basis": "중소기업 특별세액감면", "condition": "소기업, 수도권 외 제조업·출판업 등", "rate_percent": 30, "rate_label": "감면율", "source": "source.nts.corporate-tax-consulting.2026"},
    {"label": "중기업 수도권 외 제조업 등", "basis": "중소기업 특별세액감면", "condition": "중기업, 수도권 외 제조업 등", "rate_percent": 15, "rate_label": "감면율", "source": "source.nts.corporate-tax-consulting.2026"},
    {"label": "도소매·의료업 등", "basis": "중소기업 특별세액감면", "condition": "업종·지역별 차등", "rate_percent_min": 5, "rate_percent_max": 10, "rate_label": "감면율", "source": "source.nts.corporate-tax-consulting.2026"},
]


GOOD_LANDLORD_REDUCTION_CRITERIA = [
    {"label": "임대료 인하액", "basis": "상가건물 임대료 인하액", "condition": "소상공인 임차인 임대료 인하 등 요건 충족", "rate_percent": 70, "rate_label": "세액공제율", "note": "요건과 과세연도별 적용기한 확인 필요", "source": "source.nts.corporate-tax.reliefs"},
]


DEDUCTION_CRITERIA_BY_ID = {
    "deduction.personal": PERSONAL_DEDUCTION_CRITERIA,
    "deduction.personal.basic": PERSONAL_BASIC_DEDUCTION_CRITERIA,
    "deduction.personal.additional": PERSONAL_ADDITIONAL_DEDUCTION_CRITERIA,
    "deduction.pension-insurance": PENSION_INSURANCE_DEDUCTION_CRITERIA,
    "deduction.special-income": SPECIAL_INCOME_DEDUCTION_CRITERIA,
    "deduction.health-insurance-premium": HEALTH_INSURANCE_PREMIUM_DEDUCTION_CRITERIA,
    "deduction.housing-funds": HOUSING_FUNDS_DEDUCTION_CRITERIA,
    "deduction.other-income": OTHER_INCOME_DEDUCTION_CRITERIA,
    "deduction.personal-pension-savings": PERSONAL_PENSION_SAVINGS_DEDUCTION_CRITERIA,
    "deduction.small-business-mutual-aid": SMALL_BUSINESS_MUTUAL_AID_DEDUCTION_CRITERIA,
    "deduction.housing-savings": HOUSING_SAVINGS_DEDUCTION_CRITERIA,
    "deduction.investment-association": INVESTMENT_ASSOCIATION_DEDUCTION_CRITERIA,
    "deduction.employee-stock-ownership": EMPLOYEE_STOCK_OWNERSHIP_DEDUCTION_CRITERIA,
    "deduction.employment-maintenance-worker": EMPLOYMENT_MAINTENANCE_WORKER_DEDUCTION_CRITERIA,
    "deduction.long-term-fund": LONG_TERM_FUND_DEDUCTION_CRITERIA,
    "deduction.youth-long-term-fund": YOUTH_LONG_TERM_FUND_DEDUCTION_CRITERIA,
}


CREDIT_CRITERIA_BY_ID = {
    "credit.earned-income": EARNED_INCOME_TAX_CREDIT_CRITERIA,
    "credit.child": CHILD_TAX_CREDIT_CRITERIA,
    "credit.insurance-premium": INSURANCE_PREMIUM_CREDIT_CRITERIA,
    "credit.education-expense": EDUCATION_EXPENSE_CREDIT_CRITERIA,
    "credit.donation": DONATION_CREDIT_CRITERIA,
    "credit.foreign-tax-paid": FOREIGN_TAX_PAID_CREDIT_CRITERIA,
    "credit.research-and-development": RND_CREDIT_CRITERIA,
    "credit.integrated-employment": INTEGRATED_EMPLOYMENT_CREDIT_CRITERIA,
}


CORPORATE_SUPPORT_CRITERIA_BY_ID = {
    "corporate.support.startup-sme-reduction": STARTUP_SME_REDUCTION_CRITERIA,
    "corporate.support.sme-special-reduction": SME_SPECIAL_REDUCTION_CRITERIA,
    "corporate.support.tech-transfer-reduction": [
        {"label": "기술이전 소득", "basis": "기술이전 소득", "condition": "중소기업 기술이전", "rate_percent": 50, "rate_label": "감면율", "source": "source.nts.corporate-tax.reliefs"},
        {"label": "기술대여 소득", "basis": "기술대여 소득", "condition": "중소기업 기술대여", "rate_percent": 25, "rate_label": "감면율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.winwin-payment-credit": [
        {"label": "상생결제 지급금액", "basis": "상생결제 지급금액", "condition": "상생결제제도 이용 구매대금 지급", "rate_percent_min": 0.1, "rate_percent_max": 0.3, "rate_label": "세액공제율", "note": "결제기한 구간별 차등", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.wage-increase-credit": [
        {"label": "근로소득 증대", "basis": "직전 3년 평균 초과 임금증가분", "condition": "임금증가 요건 충족", "rate_percent_min": 5, "rate_percent_max": 20, "rate_label": "세액공제율", "note": "기업규모와 정규직 전환 여부별 차등", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.performance-sharing-credit": [
        {"label": "경영성과급", "basis": "성과공유 중소기업 경영성과급 지급액", "condition": "성과공유기업 요건 충족", "rate_percent": 15, "rate_label": "세액공제율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.employment-maintenance-credit": [
        {"label": "고용유지 임금감소분", "basis": "임금감소액 또는 보전액", "condition": "고용유지 요건 충족", "rate_percent": 50, "rate_label": "공제율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.social-insurance-credit": [
        {"label": "고용증가 사회보험료", "basis": "고용증가인원의 사용자 부담 사회보험료", "condition": "상시근로자 증가", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "세액공제율", "note": "청년·경력단절자 등 우대 대상과 기업규모별 차등", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.minimum-tax-preference": [
        {"label": "중소기업 최저한세", "basis": "각종 감면 전 과세표준", "condition": "중소기업", "rate_percent": 7, "rate_label": "최저한세율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.cooperation-credit": [
        {"label": "상생협력 출연금", "basis": "협력중소기업 지원 목적 출연금 등", "condition": "상생협력 지원 요건 충족", "rate_percent": 10, "rate_label": "세액공제율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.rnd-credit": RND_CREDIT_CRITERIA,
    "corporate.support.rnd-grant-deferral": [
        {"label": "연구개발출연금 과세이연", "basis": "연구개발출연금 등", "condition": "연구개발 자산 취득 또는 비용 지출", "benefit": "익금불산입 후 사용 시점에 익금산입", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.rnd-zone-reduction": [
        {"label": "연구개발특구 감면", "basis": "법인세", "condition": "연구개발특구 입주 첨단기술기업 등", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "note": "일반적으로 3년 100%, 이후 2년 50% 구조", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.ma-credit": [
        {"label": "기술혁신형 M&A", "basis": "인수가액 중 기술가치 금액", "condition": "기술혁신형 합병·주식취득", "rate_percent": 10, "rate_label": "세액공제율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.facility-investment-credit": [
        {"label": "통합투자 기본공제", "basis": "사업용 유형자산 등 투자금액", "condition": "통합투자세액공제 대상 투자", "rate_percent_min": 1, "rate_percent_max": 10, "rate_label": "기본공제율", "note": "기업규모·투자자산 유형별 차등", "source": "source.nts.corporate-tax-consulting.2026"},
        {"label": "투자증가분 추가공제", "basis": "직전 3년 평균 투자액 초과분", "condition": "투자 증가", "rate_percent": 10, "rate_label": "추가공제율", "note": "추가공제 한도는 기본공제 금액의 2배", "source": "source.nts.corporate-tax-consulting.2026"},
    ],
    "corporate.support.local-relocation-reduction": [
        {"label": "수도권 밖 이전 감면", "basis": "법인세", "condition": "공장·본사 등 지방 이전 요건 충족", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "note": "지역과 기간별 차등", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.agricultural-corporation-reduction": [
        {"label": "농업소득", "basis": "영농조합법인 등 농업소득", "condition": "농업법인 요건 충족", "rate_percent": 100, "rate_label": "면제율", "source": "source.nts.corporate-tax.reliefs"},
        {"label": "농업 외 소득", "basis": "농업 외 소득", "condition": "한도 내 감면", "rate_percent": 50, "rate_label": "감면율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.industrial-complex-reduction": [
        {"label": "농공단지 등 입주기업", "basis": "법인세", "condition": "농공단지 등 입주 후 최초 소득발생", "rate_percent": 50, "rate_label": "감면율", "note": "감면기간 요건 별도 확인", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.social-enterprise-reduction": [
        {"label": "사회적기업·장애인 표준사업장", "basis": "법인세", "condition": "인증 사회적기업 등", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "note": "일반적으로 3년 100%, 이후 2년 50% 구조", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.jeju-zone-reduction": [
        {"label": "제주첨단과학기술단지 등", "basis": "법인세", "condition": "제주첨단과학기술단지 또는 제주투자진흥지구 입주", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.enterprise-city-reduction": [
        {"label": "기업도시개발구역 창업·신설", "basis": "법인세", "condition": "기업도시개발구역 창업 또는 사업장 신설", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.e-filing-credit": [
        {"label": "전자신고 세액공제", "basis": "법인세 전자신고", "condition": "법인이 직접 전자신고", "deduction_krw": 10_000, "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.restructuring-deferral": [
        {"label": "구조조정 과세이연", "basis": "양도차익 등", "condition": "구조조정 및 재무구조개선 요건 충족", "benefit": "손금산입 또는 익금불산입으로 과세이연", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.local-relocation-deferral": [
        {"label": "지방이전 과세이연", "basis": "지방이전 관련 양도차익 등", "condition": "지방이전 촉진 요건 충족", "benefit": "손금산입 또는 익금불산입으로 과세이연", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.good-landlord-credit": GOOD_LANDLORD_REDUCTION_CRITERIA,
    "corporate.support.crisis-area-startup-reduction": [
        {"label": "위기지역 창업기업", "basis": "법인세", "condition": "위기지역 지정 또는 선포 기간 창업·사업장 신설", "rate_percent_min": 50, "rate_percent_max": 100, "rate_label": "감면율", "note": "감면기간 및 지역별 요건 별도 확인", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.disaster-loss-credit": [
        {"label": "재해손실세액공제", "basis": "재해상실자산가액 / 상실 전 자산총액", "condition": "사업용 총자산가액의 20% 이상 상실", "rate_percent": 20, "rate_label": "상실비율 문턱", "benefit": "산출세액에 재해상실비율을 곱해 공제", "source": "source.nts.corporate-tax.reliefs"},
    ],
    "corporate.support.foreign-tax-paid-credit": FOREIGN_TAX_PAID_CREDIT_CRITERIA,
}


BASIC_LIVELIHOOD_BENEFIT_CRITERIA = [
    {"label": "1인 가구 선정·급여기준", "basis": "소득인정액", "condition": "2026년 기준 중위소득 32% 이하", "threshold_krw_max": 820_556, "benefit": "생계급여 기준액에서 소득인정액 차감 지급", "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "2인 가구 선정·급여기준", "basis": "소득인정액", "condition": "2026년 기준 중위소득 32% 이하", "threshold_krw_max": 1_343_773, "benefit": "생계급여 기준액에서 소득인정액 차감 지급", "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "3인 가구 선정·급여기준", "basis": "소득인정액", "condition": "2026년 기준 중위소득 32% 이하", "threshold_krw_max": 1_714_892, "benefit": "생계급여 기준액에서 소득인정액 차감 지급", "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "4인 가구 선정·급여기준", "basis": "소득인정액", "condition": "2026년 기준 중위소득 32% 이하", "threshold_krw_max": 2_078_316, "benefit": "생계급여 기준액에서 소득인정액 차감 지급", "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "5인 가구 선정·급여기준", "basis": "소득인정액", "condition": "2026년 기준 중위소득 32% 이하", "threshold_krw_max": 2_418_150, "benefit": "생계급여 기준액에서 소득인정액 차감 지급", "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "부양의무자 고소득 제외", "basis": "부양의무자 연 소득", "condition": "1.3억원 초과 시 제외 가능", "threshold_krw": 130_000_000, "source": "source.govkr.basic-livelihood-benefit"},
    {"label": "부양의무자 일반재산 제외", "basis": "부양의무자 일반재산", "condition": "12억원 초과 시 제외 가능", "threshold_krw": 1_200_000_000, "source": "source.govkr.basic-livelihood-benefit"},
]


YOUTH_FUTURE_SAVINGS_CRITERIA = [
    {"label": "출시 예정", "basis": "상품 출시", "condition": "2026년 6월 출시 예정", "benefit": "청년 자산형성 적금", "source": "source.fsc.youth-future-savings"},
    {"label": "가입연령", "basis": "만 나이", "condition": "19세 이상 34세 이하", "note": "청년기본법상 청년 기준", "source": "source.fsc.youth-future-savings"},
    {"label": "일반형 개인소득", "basis": "개인소득", "condition": "6,000만원 이하", "threshold_krw_max": 60_000_000, "source": "source.fsc.youth-future-savings"},
    {"label": "일반형 소상공인 매출", "basis": "연매출", "condition": "3억원 이하 소상공인", "threshold_krw_max": 300_000_000, "source": "source.fsc.youth-future-savings"},
    {"label": "일반형 가구소득", "basis": "기준 중위소득", "condition": "200% 이하", "benefit": "일반형 가입 가능", "source": "source.fsc.youth-future-savings"},
    {"label": "우대형 개인소득", "basis": "개인소득", "condition": "3,600만원 이하 중소기업 재직자", "threshold_krw_max": 36_000_000, "source": "source.fsc.youth-future-savings"},
    {"label": "우대형 소상공인 매출", "basis": "연매출", "condition": "1억원 이하 소상공인", "threshold_krw_max": 100_000_000, "source": "source.fsc.youth-future-savings"},
    {"label": "우대형 가구소득", "basis": "기준 중위소득", "condition": "150% 이하", "benefit": "우대형 가입 가능", "source": "source.fsc.youth-future-savings"},
    {"label": "월 납입한도", "basis": "월 납입금", "condition": "최대 50만원 자유적립", "limit_krw": 500_000, "source": "source.fsc.youth-future-savings"},
    {"label": "일반형 기여금", "basis": "월 납입금", "condition": "일반형", "rate_percent": 6, "rate_label": "기여금비율", "benefit": "정부기여금 매칭", "source": "source.fsc.youth-future-savings"},
    {"label": "우대형 기여금", "basis": "월 납입금", "condition": "우대형", "rate_percent": 12, "rate_label": "기여금비율", "benefit": "정부기여금 매칭", "source": "source.fsc.youth-future-savings"},
    {"label": "만기", "basis": "가입기간", "condition": "3년", "benefit": "이자소득 비과세 특례 예정", "source": "source.fsc.youth-future-savings"},
]


ILLEGAL_PRIVATE_FINANCE_PREVENTION_LOAN_CRITERIA = [
    {"label": "신용요건", "basis": "개인신용평점", "condition": "하위 20%", "benefit": "신청 대상", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "소득요건", "basis": "연소득", "condition": "3,500만원 이하", "threshold_krw_max": 35_000_000, "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "필수 이수·가입", "basis": "사전요건", "condition": "금융교육 이수 또는 복지멤버십 가입", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "대출한도", "basis": "1인당 한도", "condition": "최대 100만원", "limit_krw": 1_000_000, "note": "연체자는 기본 50만원+추가 50만원, 특정용도 증빙 시 기본 최대 100만원", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "일반 금리", "basis": "대출금리", "condition": "일반", "rate_percent": 12.5, "rate_label": "금리", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "사회적배려대상자 금리", "basis": "대출금리", "condition": "사회적배려대상자", "rate_percent": 9.9, "rate_label": "금리", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
    {"label": "완제자 재대출 금리", "basis": "대출금리", "condition": "6개월 이상 이용 후 완제자 재대출", "rate_percent": 4.5, "rate_label": "금리", "source": "source.kinfa.illegal-private-finance-prevention-loan"},
]


HESSAL_LOAN_YOUTH_CRITERIA = [
    {"label": "연령·소득", "basis": "만 나이와 연소득", "condition": "19세 이상 34세 이하이면서 연소득 3,500만원 이하", "threshold_krw_max": 35_000_000, "source": "source.kinfa.hessal-loan-youth"},
    {"label": "취업준비생", "basis": "지원대상", "condition": "대학(원)생, 학점은행제 수강자, 미취업청년", "source": "source.kinfa.hessal-loan-youth"},
    {"label": "사회초년생", "basis": "지원대상", "condition": "중소기업에 1년 이하 재직 중", "source": "source.kinfa.hessal-loan-youth"},
    {"label": "청년사업자", "basis": "지원대상", "condition": "창업 1년 이하 저소득 청년 개인사업자", "source": "source.kinfa.hessal-loan-youth"},
    {"label": "동일인 한도", "basis": "보증한도", "condition": "1인 최대 1,200만원", "limit_krw": 12_000_000, "note": "상환 후에도 한도 재부여 없음", "source": "source.kinfa.hessal-loan-youth"},
    {"label": "일반생활자금 연간한도", "basis": "보증한도", "condition": "연간 600만원", "limit_krw": 6_000_000, "source": "source.kinfa.hessal-loan-youth"},
    {"label": "특정용도자금 연간한도", "basis": "보증한도", "condition": "연간 900만원", "limit_krw": 9_000_000, "source": "source.kinfa.hessal-loan-youth"},
]


HESSAL_119_CRITERIA = [
    {"label": "채무조정 이용기간", "basis": "은행권 채무조정 프로그램", "condition": "3개월 이상 이용 중", "source": "source.kinfa.hessal-119"},
    {"label": "성실상환", "basis": "상환상태", "condition": "신청일 현재 연체 중이 아님", "source": "source.kinfa.hessal-119"},
    {"label": "연매출", "basis": "개인사업자 연 매출", "condition": "3억원 이하", "threshold_krw_max": 300_000_000, "source": "source.kinfa.hessal-119"},
    {"label": "대출한도", "basis": "신규·추가 운전자금", "condition": "최대 2,000만원", "limit_krw": 20_000_000, "note": "신규 1,000만원 + 추가 1,000만원", "source": "source.kinfa.hessal-119"},
    {"label": "대출금리", "basis": "은행별 대출금리", "condition": "연 6~7% 수준", "rate_percent_min": 6, "rate_percent_max": 7, "rate_label": "금리", "source": "source.kinfa.hessal-119"},
    {"label": "보증료", "basis": "보증료율", "condition": "연 0.5%", "rate_percent": 0.5, "rate_label": "보증료율", "source": "source.kinfa.hessal-119"},
]


DIDIMDOL_LOAN_CRITERIA = [
    {"label": "순자산", "basis": "본인 및 배우자 합산 순자산", "condition": "5.11억원 이하", "threshold_krw_max": 511_000_000, "source": "source.hf.didimdol-loan"},
    {"label": "주택가격", "basis": "공부상 주택 평가액", "condition": "5억원 이하", "threshold_krw_max": 500_000_000, "note": "신혼·2자녀 이상 가구는 6억원 이하", "source": "source.hf.didimdol-loan"},
    {"label": "기본 소득요건", "basis": "부부합산 연소득", "condition": "6,000만원 이하", "threshold_krw_max": 60_000_000, "source": "source.hf.didimdol-loan"},
    {"label": "생애최초·2자녀 이상 소득요건", "basis": "부부합산 연소득", "condition": "7,000만원 이하", "threshold_krw_max": 70_000_000, "source": "source.hf.didimdol-loan"},
    {"label": "신혼가구 소득요건", "basis": "부부합산 연소득", "condition": "8,500만원 이하", "threshold_krw_max": 85_000_000, "source": "source.hf.didimdol-loan"},
    {"label": "대출한도", "basis": "대출한도", "condition": "최대 2억원", "limit_krw": 200_000_000, "note": "생애최초 2.4억원, 신혼·2자녀 이상 3.2억원", "source": "source.hf.didimdol-loan"},
    {"label": "LTV", "basis": "담보인정비율", "condition": "최대 70%", "rate_percent": 70, "rate_label": "LTV", "source": "source.hf.didimdol-loan"},
    {"label": "DTI", "basis": "총부채상환비율", "condition": "최대 60%", "rate_percent": 60, "rate_label": "DTI", "source": "source.hf.didimdol-loan"},
    {"label": "2026년 5월 금리", "basis": "소득구간·만기별 금리", "condition": "연 2.85%~4.15%", "rate_percent_min": 2.85, "rate_percent_max": 4.15, "rate_label": "금리", "source": "source.hf.didimdol-rate.2026-05"},
]


YOUTH_SPECIAL_RENT_GUARANTEE_CRITERIA = [
    {"label": "무주택 청년 연령", "basis": "신청일 기준 만 나이", "condition": "만 34세 이하", "source": "source.hf.special-rent-guarantee"},
    {"label": "무주택 청년 소득", "basis": "본인과 배우자 합산 연소득", "condition": "7,000만원 이하", "threshold_krw_max": 70_000_000, "source": "source.hf.special-rent-guarantee"},
    {"label": "무주택 청년 보증한도", "basis": "보증한도", "condition": "최대 2억원", "limit_krw": 200_000_000, "note": "1억원 이하 이용 시 상환능력별 보증한도 생략, 보증비율 100%", "source": "source.hf.special-rent-guarantee"},
    {"label": "다자녀가구 보증한도", "basis": "보증한도", "condition": "미성년 자녀 2명 이상", "limit_krw": 200_000_000, "source": "source.hf.special-rent-guarantee"},
]


LONG_TERM_DELINQUENT_DEBT_ADJUSTMENT_CRITERIA = [
    {"label": "연체기간", "basis": "채무조정 신청일 기준 연체채무", "condition": "5년 이상", "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "1인 가구 소득", "basis": "2026년 기준중위소득 125%", "condition": "3,205,298원 이하", "threshold_krw_max": 3_205_298, "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "2인 가구 소득", "basis": "2026년 기준중위소득 125%", "condition": "5,249,115원 이하", "threshold_krw_max": 5_249_115, "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "3인 가구 소득", "basis": "2026년 기준중위소득 125%", "condition": "6,698,795원 이하", "threshold_krw_max": 6_698_795, "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "4인 가구 소득", "basis": "2026년 기준중위소득 125%", "condition": "8,118,423원 이하", "threshold_krw_max": 8_118_423, "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "채무감면", "basis": "연체이자·이자·원금", "condition": "연체이자 및 이자 전액 감면, 원금 최대 30~80% 감면", "rate_percent_min": 30, "rate_percent_max": 80, "rate_label": "감면율", "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "분할상환", "basis": "상환기간", "condition": "최장 10년 이내 원금균등분할상환", "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
    {"label": "상환유예", "basis": "유예기간·유예이자율", "condition": "최장 3년 이내 유예, 유예이자율 연 2%", "rate_percent": 2, "rate_label": "유예이자율", "source": "source.ccrs.long-term-delinquent-debt-adjustment"},
]


NO_FIXED_AMOUNT = "정액 금액 기준 없음"
RATE_ONLY_AMOUNT = "비율 기준이며 고정 원화 금액 없음"


RETIREMENT_INCOME_TAX_CRITERIA = [
    {"label": "퇴직소득세 계산 산식", "basis": "퇴직소득 과세표준", "condition": "2020년 이후 퇴직분", "amount_formula": "(과세표준 × 기본세율 - 누진공제액) ÷ 12 × 근속연수", "source": "source.nts.retirement-income.calculation"},
    {"label": "근속연수 5년 이하 공제", "basis": "근속연수공제", "condition": "5년 이하", "amount_formula": "근속연수 × 1,000,000원", "source": "source.nts.retirement-income.calculation"},
    {"label": "근속연수 10년 이하 공제", "basis": "근속연수공제", "condition": "5년 초과 10년 이하", "amount_formula": "5,000,000원 + (근속연수 - 5년) × 2,000,000원", "source": "source.nts.retirement-income.calculation"},
    {"label": "근속연수 20년 이하 공제", "basis": "근속연수공제", "condition": "10년 초과 20년 이하", "amount_formula": "15,000,000원 + (근속연수 - 10년) × 2,500,000원", "source": "source.nts.retirement-income.calculation"},
    {"label": "근속연수 20년 초과 공제", "basis": "근속연수공제", "condition": "20년 초과", "amount_formula": "40,000,000원 + (근속연수 - 20년) × 3,000,000원", "source": "source.nts.retirement-income.calculation"},
]


STAMP_TAX_CRITERIA = [
    {"label": "1천만원 이하", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "1천만원 이하", "amount_krw": 0, "source": "source.law.stamp-tax-act.article3"},
    {"label": "1천만원 초과 3천만원 이하", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "1천만원 초과 3천만원 이하", "threshold_krw_min": 10_000_000, "threshold_krw_max": 30_000_000, "amount_krw": 20_000, "source": "source.law.stamp-tax-act.article3"},
    {"label": "3천만원 초과 5천만원 이하", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "3천만원 초과 5천만원 이하", "threshold_krw_min": 30_000_000, "threshold_krw_max": 50_000_000, "amount_krw": 40_000, "source": "source.law.stamp-tax-act.article3"},
    {"label": "5천만원 초과 1억원 이하", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "5천만원 초과 1억원 이하", "threshold_krw_min": 50_000_000, "threshold_krw_max": 100_000_000, "amount_krw": 70_000, "source": "source.law.stamp-tax-act.article3"},
    {"label": "1억원 초과 10억원 이하", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "1억원 초과 10억원 이하", "threshold_krw_min": 100_000_000, "threshold_krw_max": 1_000_000_000, "amount_krw": 150_000, "source": "source.law.stamp-tax-act.article3"},
    {"label": "10억원 초과", "basis": "부동산 등 소유권 이전 과세문서 기재금액", "condition": "10억원 초과", "threshold_krw_min": 1_000_000_000, "amount_krw": 350_000, "source": "source.law.stamp-tax-act.article3"},
]


NATIONAL_SPECIAL_TAX_CRITERIA_BY_ID = {
    "tax.income.retirement": RETIREMENT_INCOME_TAX_CRITERIA,
    "tax.individual-consumption": [
        {"label": "과세물품·장소별 세율", "basis": "과세가격 또는 과세수량", "condition": "개별소비세법상 과세물품·장소·행위", "amount_formula": "과세가격 × 품목별 세율 또는 과세수량 × 품목별 정액세", "source": "source.law.individual-consumption-tax-act.rates"},
    ],
    "tax.transport-energy-environment": [
        {"label": "유류 등 과세물품별 정액세", "basis": "과세물품 수량", "condition": "휘발유·경유 등 법정 과세물품", "amount_formula": "과세물품 수량 × 물품별 정액세율", "source": "source.law.transport-energy-environment-tax-act.rates"},
    ],
    "tax.liquor": [
        {"label": "주류 종류별 세율", "basis": "주류 가격 또는 출고수량", "condition": "주정·탁주·맥주·증류주 등 주류 종류별", "amount_formula": "과세표준 × 종가세율 또는 출고수량 × 종량세율", "source": "source.law.liquor-tax-act.rates"},
    ],
    "tax.stamp": STAMP_TAX_CRITERIA,
    "tax.securities-transaction": [
        {"label": "주권 양도 거래", "basis": "주권 등 양도가액", "condition": "주권 또는 지분 양도", "amount_formula": "양도가액 × 증권거래세법·시행령상 시장별 세율", "source": "source.law.securities-transaction-tax-act.article8"},
    ],
    "tax.education": [
        {"label": "교육세 부가 과세", "basis": "개별소비세액·교통세액·금융보험업 수익금액 등", "condition": "교육세법상 납세의무자", "amount_formula": "교육세 과세표준 × 교육세법상 세율", "source": "source.law.education-tax-act.article5"},
    ],
    "tax.special-rural-development": [
        {"label": "농어촌특별세 부가 과세", "basis": "감면세액·증권거래금액·개별소비세액 등", "condition": "농어촌특별세법상 납세의무자", "amount_formula": "과세표준 × 농어촌특별세법상 세율", "source": "source.law.special-rural-development-tax-act.article5"},
    ],
    "tax.customs": [
        {"label": "수입물품 관세", "basis": "수입물품 과세가격", "condition": "품목분류별 관세율표 적용", "amount_formula": "과세가격 × 품목별 관세율", "source": "source.law.customs-tariff"},
    ],
}


LOCAL_TAX_CRITERIA_BY_ID = {
    "local.acquisition": [
        {"label": "취득세 산식", "basis": "취득가액 또는 시가표준액", "condition": "부동산·차량 등 과세물건 취득", "amount_formula": "과세표준 × 과세대상별 취득세율", "source": "source.law.local-tax-act.rates"},
    ],
    "local.registration-license": [
        {"label": "등록면허세 산식", "basis": "등록가액 또는 면허 종류", "condition": "등기·등록 또는 면허", "amount_formula": "등록가액 × 등록세율 또는 면허종별 정액세", "source": "source.law.local-tax-act.rates"},
    ],
    "local.leisure": [
        {"label": "레저세 세율", "basis": "승자투표권·승마투표권 발매금 총액", "condition": "경륜·경정·경마 등", "rate_percent": 10, "amount_formula": "발매금 총액 × 10%", "source": "source.law.local-tax-act.rates"},
    ],
    "local.tobacco-consumption": [
        {"label": "궐련 담배소비세", "basis": "궐련 20개비", "condition": "궐련 담배 반출 또는 반입", "amount_krw": 1_007, "source": "source.law.local-tax-act.rates"},
    ],
    "local.local-consumption": [
        {"label": "지방소비세 산식", "basis": "부가가치세액", "condition": "부가가치세와 연동", "amount_formula": "부가가치세액 × 지방세법상 지방소비세율", "source": "source.law.local-tax-act.rates"},
    ],
    "local.resident": [
        {"label": "주민세 산식", "basis": "개인분·사업소분·종업원분 과세표준", "condition": "지방자치단체 조례와 지방세법 기준 적용", "amount_formula": "개인분 정액세 또는 사업소 연면적·종업원 급여총액 기준 산식", "source": "source.law.local-tax-act.rates"},
    ],
    "local.local-income": [
        {"label": "지방소득세 산식", "basis": "개인·법인 소득 과세표준", "condition": "소득세·법인세와 연결", "amount_formula": "지방소득세 과세표준 × 지방세법상 세율", "source": "source.law.local-tax-act.rates"},
    ],
    "local.automobile": [
        {"label": "자동차세 산식", "basis": "차종·용도·배기량 또는 적재량", "condition": "자동차 보유", "amount_formula": "차종별 과세단위 × 지방세법상 단위세액", "source": "source.law.local-tax-act.rates"},
    ],
    "local.regional-resource-facility": [
        {"label": "지역자원시설세 산식", "basis": "특정자원·특정부동산·소방분 과세표준", "condition": "지역자원 보호 또는 소방시설 재원 목적", "amount_formula": "과세대상별 과세표준 × 지방세법상 세율 또는 정액세", "source": "source.law.local-tax-act.rates"},
    ],
    "local.local-education": [
        {"label": "지방교육세 부가 과세", "basis": "취득세액·등록면허세액·레저세액 등", "condition": "지방교육재정 확충 목적", "amount_formula": "본세액 × 지방교육세율", "source": "source.law.local-tax-act.rates"},
    ],
}


CONCEPT_CRITERIA_BY_ID = {
    "concept.capital-gains.calculation-flow": [
        {"label": "양도소득 과세표준 산식", "basis": "양도가액·취득가액·필요경비·공제", "condition": "양도소득이 발생한 경우", "amount_formula": "양도가액 - 취득가액 - 필요경비 - 장기보유특별공제 - 양도소득 기본공제", "source": "source.nts.capital-gains.overview"},
        {"label": "양도소득 기본공제", "basis": "자산군별 양도소득금액", "condition": "해당 과세기간 자산군별 적용", "deduction_krw": 2_500_000, "source": "source.nts.capital-gains.basic-deduction"},
    ],
    "concept.capital-gains.stock-basic-deduction": [
        {"label": "주식 등 양도소득 기본공제", "basis": "주식 등 양도소득금액", "condition": "해당 과세기간 주식 등 그룹", "deduction_krw": 2_500_000, "source": "source.nts.capital-gains.basic-deduction"},
    ],
    "concept.cre-tax-base-date": [
        {"label": "과세기준일", "basis": "보유일 기준", "condition": "매년 6월 1일 현재 보유", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.comprehensive-real-estate.overview"},
    ],
}


FILING_CRITERIA_BY_ID = {
    "filing.income-tax-return": [
        {"label": "확정신고 기간", "basis": "신고·납부기한", "condition": "다음연도 5월 1일부터 5월 31일까지", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.income-tax.deadline"},
    ],
    "filing.year-end-settlement": [
        {"label": "연말정산 계산", "basis": "근로소득세 확정 절차", "condition": "원천징수의무자가 해당 과세기간 근로소득세를 정산", "amount_formula": "결정세액 - 기납부세액", "source": "source.nts.year-end-settlement.calculation"},
    ],
    "filing.business-registration": [
        {"label": "사업자등록 신청기한", "basis": "사업 개시일", "condition": "사업 개시 전 또는 사업 개시일부터 20일 이내", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.business-registration.application"},
    ],
    "filing.withholding-tax": [
        {"label": "원천세 월별 납부", "basis": "원천징수일", "condition": "징수일이 속하는 달의 다음달 10일까지", "amount_formula": "원천징수 대상 지급액 × 소득별 원천징수세율", "source": "source.nts.withholding.overview"},
    ],
    "filing.vat-return": [
        {"label": "일반과세자 확정신고", "basis": "부가가치세 과세기간", "condition": "제1기·제2기 확정신고 납부", "amount_formula": "매출세액 - 매입세액 - 공제세액", "source": "source.nts.vat.filing-duty"},
        {"label": "간이과세자 연간 신고", "basis": "직전연도 공급대가", "condition": "간이과세자 과세기간 신고", "amount_formula": "매출액 × 업종별 부가가치율 × 10% - 공제세액", "source": "source.nts.vat.filing-duty"},
    ],
    "filing.capital-gains-return": [
        {"label": "양도소득세 예정신고", "basis": "양도일이 속하는 달의 말일", "condition": "자산 유형별 예정신고 기한 적용", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.capital-gains.deadline"},
        {"label": "양도소득세 확정신고", "basis": "과세기간 다음연도 5월", "condition": "예정신고 대상 외 확정신고 필요 여부 확인", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.capital-gains.deadline"},
    ],
    "filing.inheritance-tax-return": [
        {"label": "상속세 신고기한", "basis": "상속개시일이 속하는 달의 말일", "condition": "거주자 6개월, 비거주자 9개월", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.inheritance.overview"},
    ],
    "filing.gift-tax-return": [
        {"label": "증여세 신고기한", "basis": "증여받은 날이 속하는 달의 말일", "condition": "일반 증여 3개월", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.gift.deadline"},
    ],
    "filing.grant-application": [
        {"label": "근로·자녀장려금 정기신청", "basis": "2025년 귀속 소득", "condition": "2026년 5월 정기신청", "amount_applicability": NO_FIXED_AMOUNT, "source": "source.nts.grant.deadline"},
    ],
}


ISA_CRITERIA = [
    {"label": "연 납입한도", "basis": "ISA 납입금", "condition": "연간 납입한도", "limit_krw": 20_000_000, "source": "source.fsc.isa.policy"},
    {"label": "총 납입한도", "basis": "ISA 납입금", "condition": "5년 누적 한도", "limit_krw": 100_000_000, "source": "source.fsc.isa.policy"},
    {"label": "일반형 비과세", "basis": "계좌 순소득", "condition": "일반형 ISA", "limit_krw": 2_000_000, "benefit": "한도 내 비과세", "source": "source.moef.isa.tax-benefit"},
    {"label": "서민·농어민형 비과세", "basis": "계좌 순소득", "condition": "서민·농어민형 ISA", "limit_krw": 4_000_000, "benefit": "한도 내 비과세", "source": "source.moef.isa.tax-benefit"},
    {"label": "비과세 초과분 분리과세", "basis": "비과세 한도 초과 순소득", "condition": "비과세 한도 초과분", "rate_percent": 9, "rate_label": "분리과세율", "amount_formula": "비과세 한도 초과 순소득 × 9%", "source": "source.moef.isa.tax-benefit"},
]


SUPPORT_CRITERIA_BY_ID = {
    "support.isa": ISA_CRITERIA,
}


ITEM_CRITERIA_BY_ID = {
    **NATIONAL_SPECIAL_TAX_CRITERIA_BY_ID,
    **LOCAL_TAX_CRITERIA_BY_ID,
    **CONCEPT_CRITERIA_BY_ID,
    **FILING_CRITERIA_BY_ID,
    **SUPPORT_CRITERIA_BY_ID,
}


NODES = [
    node(
        "kr-tax-system",
        "OpenTax",
        "domain",
        "대한민국의 세금, 공제, 감면, 정책지원금, 신고·납부 기한을 Obsidian 지식 그래프로 학습하기 위한 OpenTax 최상위 항목입니다.",
        "00_Index",
        children=["category.national-taxes", "category.customs", "category.local-taxes", "category.deductions-and-reliefs", "category.policy-supports", "category.business-tax-compliance", "category.filing-calendar"],
        sources=["source.national-tax-framework-act.2026.article2", "source.local-tax-framework-act.2026.article8"],
        terms=["term.national-tax", "term.local-tax", "term.tax-law"],
        tags=["root"],
    ),
    node("category.national-taxes", "국세", "category", "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목 전체입니다.", "10_Taxes/National", parents=["kr-tax-system"], children=NATIONAL_TAX_IDS, sources=["source.national-tax-framework-act.2026.article2"], terms=["term.national-tax"], law_reference="국세기본법 제2조 제1호", tags=["complete-manifest"]),
    node("category.customs", "관세 영역", "category", "국세기본법 제2조의 국세 열거와 별개로 관세법에 근거해 수입물품에 부과되는 조세 영역입니다.", "10_Taxes/Customs", parents=["kr-tax-system"], children=["tax.customs"], sources=["source.customs-act.2026.article14"], terms=["term.customs"], law_reference="관세법 제14조"),
    node("category.local-taxes", "지방세", "category", "지방자치단체가 과세권을 가지는 지방세기본법 제8조상 세목 전체입니다.", "10_Taxes/Local", parents=["kr-tax-system"], children=["category.local-ordinary-taxes", "category.local-purpose-taxes"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"], law_reference="지방세기본법 제8조", tags=["complete-manifest"]),
    node("category.local-ordinary-taxes", "지방 보통세", "category", "지방세 중 특정 목적세가 아닌 보통세 세목 묶음입니다.", "10_Taxes/Local", parents=["category.local-taxes"], children=["local.acquisition", "local.registration-license", "local.leisure", "local.tobacco-consumption", "local.local-consumption", "local.resident", "local.local-income", "local.property", "local.automobile"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"]),
    node("category.local-purpose-taxes", "지방 목적세", "category", "지방세 중 특정 재원 목적을 위해 부과되는 목적세 세목 묶음입니다.", "10_Taxes/Local", parents=["category.local-taxes"], children=["local.regional-resource-facility", "local.local-education"], sources=["source.local-tax-framework-act.2026.article8"], terms=["term.local-tax"]),
    node("category.deductions-and-reliefs", "공제·감면", "category", "과세표준을 줄이는 소득공제, 산출세액에서 차감하는 세액공제, 정책 목적의 세액감면과 법인세 조세지원 항목입니다.", "20_Deductions", parents=["kr-tax-system"], children=["category.income-deductions", "category.tax-credits", "category.tax-reductions", "category.corporate-tax-supports"], sources=["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"], terms=["term.income-deduction", "term.tax-credit", "term.tax-reduction"]),
    node("category.policy-supports", "정책지원금·세제지원 계좌", "category", "국세청 현금성 지원금, 정부24 복지급여, 금융위원회·금융공공기관의 자산형성·서민금융·주거금융·채무조정 지원을 학습용으로 묶은 항목입니다.", "30_Supports", parents=["kr-tax-system"], children=["support.earned-income-tax-credit", "support.child-tax-credit", "support.basic-livelihood-benefit", "support.youth-future-savings", "support.youth-leap-account", "support.isa", "support.illegal-private-finance-prevention-loan", "support.hessal-loan-youth", "support.hessal-119", "support.didimdol-loan", "support.youth-special-rent-guarantee", "support.long-term-delinquent-debt-adjustment"], sources=["source.nts.eitc.intro", "source.nts.ctc.intro", "source.govkr.basic-livelihood-benefit", "source.fsc.youth-future-savings", "source.kinfa.youth-leap", "source.kinfa.illegal-private-finance-prevention-loan", "source.kinfa.hessal-loan-youth", "source.kinfa.hessal-119", "source.hf.didimdol-loan", "source.hf.special-rent-guarantee", "source.ccrs.long-term-delinquent-debt-adjustment", "source.fsc.isa.policy"], terms=["term.total-income", "term.gross-pay", "term.property-requirement", "term.eligibility-threshold", "term.median-income", "term.policy-finance", "term.policy-loan", "term.debt-adjustment"]),
    node("category.business-tax-compliance", "사업자 세무", "category", "개인사업자와 원천징수의무자가 사업자등록, 부가가치세, 원천세 신고·납부에서 확인해야 하는 실무 흐름입니다.", "60_Business", parents=["kr-tax-system"], children=["filing.business-registration", "filing.vat-return", "filing.withholding-tax", "filing.business-income-withholding"], sources=["source.nts.business-registration.application", "source.nts.vat.filing-duty", "source.nts.withholding.overview", "source.nts.business-income.withholding"], terms=["term.general-vat-taxpayer", "term.simple-vat-taxpayer", "term.withholding-obligor"]),
    node("category.filing-calendar", "신고·납부·신청 기한", "category", "세목과 지원제도에 연결되는 기준연도별 기한입니다.", "50_Deadlines", parents=["kr-tax-system"], children=["filing.income-tax-return", "filing.year-end-settlement", "filing.withholding-tax", "filing.vat-return", "filing.capital-gains-return", "filing.inheritance-tax-return", "filing.gift-tax-return", "filing.grant-application"], sources=["source.nts.income-tax.deadline", "source.nts.tax-calendar.2026", "source.nts.grant.deadline", "source.nts.capital-gains.deadline", "source.nts.inheritance.overview", "source.nts.gift.deadline"], terms=["term.deadline", "term.deadline-special-rule"]),
    national_tax("tax.income", "소득세", "개인의 소득에 과세되는 국세입니다. 종합소득, 퇴직소득, 양도소득 흐름으로 세부 학습 노드를 둡니다.", children=["tax.income.comprehensive", "tax.income.retirement", "tax.income.capital-gains"], related=["category.income-deductions", "category.tax-credits"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.income-tax.rates"], deadlines=["deadline.income-tax.2025-return", "deadline.year-end-settlement"], terms=["term.national-tax", "term.tax-law", "term.tax-base", "term.tax-rate", "term.progressive-deduction"], criteria=INCOME_TAX_RATE_CRITERIA),
    national_tax("tax.corporate", "법인세", "법인의 각 사업연도 소득 등에 과세되는 국세이며 법인세 공제·감면 지원제도와 직접 연결됩니다.", related=["category.corporate-tax-supports"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.corporate-tax.rates"], terms=["term.national-tax", "term.tax-law", "term.tax-base", "term.tax-rate", "term.progressive-deduction"], criteria=CORPORATE_TAX_RATE_CRITERIA),
    national_tax("tax.inheritance-and-gift", "상속세와 증여세", "상속 또는 증여로 이전되는 재산에 과세되는 국세입니다.", children=["tax.inheritance", "tax.gift"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.inheritance.overview", "source.nts.gift.deadline", "source.nts.inheritance.rates", "source.nts.gift.rates"], deadlines=["deadline.inheritance.resident", "deadline.gift.general"], terms=["term.national-tax", "term.tax-law", "term.heir", "term.donee", "term.tax-rate", "term.progressive-deduction"], criteria=INHERITANCE_GIFT_RATE_CRITERIA),
    national_tax("tax.comprehensive-real-estate", "종합부동산세", "일정 기준을 넘는 주택·토지 보유에 대해 과세되는 국세입니다.", children=["concept.cre-tax-base-date", "concept.cre-deduction-thresholds"], related=["local.property"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.comprehensive-real-estate.overview", "source.nts.comprehensive-real-estate.rates", "source.nts.real-estate-tax.faq"], terms=["term.national-tax", "term.tax-law", "term.publicly-notified-price", "term.tax-rate", "term.eligibility-threshold"], criteria=CRE_CRITERIA),
    national_tax("tax.value-added", "부가가치세", "재화 또는 용역의 공급 과정에서 생긴 부가가치에 과세되는 국세입니다.", children=["concept.general-vat-taxpayer", "concept.simple-vat-taxpayer", "concept.vat-payment-exemption"], related=["category.business-tax-compliance"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.vat.overview", "source.nts.vat.filing-duty"], deadlines=["deadline.vat.periodic", "deadline.vat.general.first-final", "deadline.vat.general.second-final", "deadline.vat.simplified.annual"], terms=["term.national-tax", "term.tax-period", "term.general-vat-taxpayer", "term.simple-vat-taxpayer", "term.tax-rate", "term.eligibility-threshold"], criteria=VAT_CRITERIA),
    national_tax("tax.individual-consumption", "개별소비세", "특정 물품, 장소, 행위 등에 개별적으로 부과되는 국세입니다."),
    national_tax("tax.transport-energy-environment", "교통·에너지·환경세", "교통시설, 에너지, 환경 관련 재원 목적의 국세입니다."),
    national_tax("tax.liquor", "주세", "주류에 과세되는 국세입니다."),
    national_tax("tax.stamp", "인지세", "과세문서 작성에 대해 부과되는 국세입니다."),
    national_tax("tax.securities-transaction", "증권거래세", "주권 등의 양도 거래에 과세되는 국세입니다.", related=["tax.income.capital-gains"]),
    national_tax("tax.education", "교육세", "교육재정 확충을 위한 목적세 성격의 국세입니다.", related=["local.local-education"]),
    national_tax("tax.special-rural-development", "농어촌특별세", "농어촌 경쟁력 강화 재원 등을 위해 부과되는 목적세 성격의 국세입니다."),
    node("tax.customs", "관세", "tax", "수입물품에 부과되는 조세입니다. 국세기본법 제2조의 국세 열거와 별도로 관세법 제14조를 근거로 관리합니다.", "10_Taxes/Customs", parents=["category.customs"], sources=["source.customs-act.2026.article14"], terms=["term.customs", "term.tax-base"], law_reference="관세법 제14조", basis_year=2026),
    node("tax.income.comprehensive", "종합소득세", "tax", "이자·배당·사업·근로·연금·기타소득 등 종합소득금액에 대해 확정신고하는 소득세 흐름입니다.", "10_Taxes/National", parents=["tax.income"], sources=["source.nts.income-tax.deadline", "source.nts.income-tax.rates"], deadlines=["deadline.income-tax.2025-return"], terms=["term.tax-base", "term.tax-rate", "term.progressive-deduction", "term.deadline-special-rule"], basis_year=2025, criteria=INCOME_TAX_RATE_CRITERIA),
    node("tax.income.retirement", "퇴직소득세", "tax", "퇴직으로 받는 소득에 대해 별도 계산 구조를 가지는 소득세입니다.", "10_Taxes/National", parents=["tax.income"], sources=["source.national-tax-framework-act.2026.article2"], terms=["term.withholding"], basis_year=2026),
    node("tax.income.capital-gains", "양도소득세", "tax", "부동산, 주식 등 자산 양도차익에 대해 과세되는 소득세입니다. 자산 유형별 특례세율이 있으므로 기본세율과 특례세율을 분리해 확인합니다.", "10_Taxes/National", parents=["tax.income"], children=["concept.capital-gains.calculation-flow", "concept.capital-gains.stock-basic-deduction", "filing.capital-gains-return"], related=["tax.securities-transaction"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.capital-gains.overview", "source.nts.capital-gains.deadline", "source.nts.capital-gains.rates"], terms=["term.tax-base", "term.capital-gain", "term.tax-rate", "term.deadline"], deadlines=["deadline.capital-gains.preliminary", "deadline.capital-gains.final"], basis_year=2026, criteria=INCOME_TAX_RATE_CRITERIA + [{"label": "국외 중소기업주식 등", "basis": "양도소득 과세표준", "condition": "국외 중소기업주식 등", "rate_percent": 10, "source": "source.nts.capital-gains.rates"}, {"label": "국외 그 밖의 주식 등", "basis": "양도소득 과세표준", "condition": "국외 그 밖의 주식 등", "rate_percent": 20, "source": "source.nts.capital-gains.rates"}, {"label": "파생상품 등", "basis": "양도소득 과세표준", "condition": "2018.4.1. 이후 양도분", "rate_percent": 10, "note": "기본세율 20%에 한시적 탄력세율 적용", "source": "source.nts.capital-gains.rates"}]),
    node("tax.inheritance", "상속세", "tax", "사망으로 이전되는 재산에 과세되는 세금입니다.", "10_Taxes/National", parents=["tax.inheritance-and-gift"], children=["filing.inheritance-tax-return"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.inheritance.overview", "source.nts.inheritance.rates"], terms=["term.tax-base", "term.heir", "term.tax-rate", "term.progressive-deduction"], deadlines=["deadline.inheritance.resident", "deadline.inheritance.nonresident"], basis_year=2026, criteria=INHERITANCE_GIFT_RATE_CRITERIA),
    node("tax.gift", "증여세", "tax", "무상 이전되는 재산에 과세되는 세금입니다.", "10_Taxes/National", parents=["tax.inheritance-and-gift"], children=["filing.gift-tax-return"], sources=["source.national-tax-framework-act.2026.article2", "source.nts.gift.deadline", "source.nts.gift.rates"], terms=["term.tax-base", "term.donee", "term.tax-rate", "term.progressive-deduction"], deadlines=["deadline.gift.general"], basis_year=2026, criteria=GIFT_RATE_CRITERIA),
    local_tax("local.acquisition", "취득세", "부동산, 차량 등 과세물건 취득에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.registration-license", "등록면허세", "재산권 등 등록 또는 각종 면허에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.leisure", "레저세", "경륜·경정·경마 등 승자투표권 발매 등에 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.tobacco-consumption", "담배소비세", "담배 반출 또는 반입에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.local-consumption", "지방소비세", "부가가치세와 연결되는 지방 보통세입니다.", "category.local-ordinary-taxes", related=["tax.value-added"]),
    local_tax("local.resident", "주민세", "개인, 사업소, 종업원 등 지역 구성원에게 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.local-income", "지방소득세", "소득세·법인세 과세표준이 되는 소득과 연결되는 지방 보통세입니다.", "category.local-ordinary-taxes", related=["tax.income", "tax.corporate"]),
    local_tax("local.property", "재산세", "토지, 건축물, 주택 등 재산 보유에 대해 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes", related=["tax.comprehensive-real-estate"], sources=["source.local-tax-framework-act.2026.article8", "source.nts.real-estate-tax.faq"], terms=["term.local-tax", "term.publicly-notified-price", "term.tax-rate"], criteria=LOCAL_PROPERTY_TAX_CRITERIA),
    local_tax("local.automobile", "자동차세", "자동차 보유 또는 주행 등에 과세되는 지방 보통세입니다.", "category.local-ordinary-taxes"),
    local_tax("local.regional-resource-facility", "지역자원시설세", "지역자원 보호, 안전관리 등 특정 재원 목적의 지방 목적세입니다.", "category.local-purpose-taxes"),
    local_tax("local.local-education", "지방교육세", "지방교육재정 확충을 위해 다른 지방세에 부가되는 지방 목적세입니다.", "category.local-purpose-taxes", related=["tax.education"]),
    node("category.income-deductions", "소득공제", "category", "근로소득 연말정산에서 과세표준 전 단계에 반영되는 공제 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.deductions-and-reliefs"], children=["deduction.personal", "deduction.pension-insurance", "deduction.special-income", "deduction.other-income"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit"], terms=["term.income-deduction", "term.deduction-limit"]),
    node("deduction.personal", "인적공제", "deduction", "기본공제와 추가공제로 구성되는 소득공제입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.personal.basic", "deduction.personal.additional"], sources=["source.nts.year-end-settlement.calculation"], terms=["term.income-deduction"], criteria=PERSONAL_DEDUCTION_CRITERIA),
    deduction("deduction.personal.basic", "기본공제", "본인, 배우자, 부양가족 등 기본공제 대상자에 대한 인적공제입니다.", "deduction.personal"),
    deduction("deduction.personal.additional", "추가공제", "경로우대, 장애인, 부녀자, 한부모 등 추가 요건에 따른 인적공제입니다.", "deduction.personal"),
    deduction("deduction.pension-insurance", "연금보험료공제", "공적연금의 근로자 부담금을 차감소득금액 계산에 반영하는 공제입니다.", "category.income-deductions"),
    node("deduction.special-income", "특별소득공제", "deduction", "근로소득 연말정산 계산 구조에서 차감소득금액을 산출할 때 반영되는 특별소득공제 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.health-insurance-premium", "deduction.housing-funds"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.deduction-limit", "source.nts.housing-rent-principal-deduction", "source.nts.housing-mortgage-interest-deduction"], terms=["term.income-deduction", "term.deduction-limit"], criteria=SPECIAL_INCOME_DEDUCTION_CRITERIA),
    deduction("deduction.health-insurance-premium", "보험료공제", "국민건강보험료, 고용보험료 등 법정 보험료 납부액을 특별소득공제로 반영하는 항목입니다.", "deduction.special-income"),
    deduction("deduction.housing-funds", "주택자금공제", "주택임차차입금 원리금상환액과 장기주택저당차입금 이자상환액 등 주택자금 관련 소득공제입니다.", "deduction.special-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    node("deduction.other-income", "그 밖의 소득공제", "deduction", "과세표준 계산 전 추가로 반영되는 소득공제 항목 묶음입니다.", "20_Deductions/IncomeDeductions", parents=["category.income-deductions"], children=["deduction.personal-pension-savings", "deduction.small-business-mutual-aid", "deduction.housing-savings", "deduction.investment-association", "deduction.credit-card-use", "deduction.employee-stock-ownership", "deduction.employment-maintenance-worker", "deduction.long-term-fund", "deduction.youth-long-term-fund"], sources=["source.nts.year-end-settlement.deduction-limit", "source.nts.housing-savings-deduction"], terms=["term.income-deduction", "term.deduction-limit"], criteria=OTHER_INCOME_DEDUCTION_CRITERIA),
    deduction("deduction.personal-pension-savings", "개인연금저축 소득공제", "연금저축 세액공제와 구분되는 개인연금저축 관련 소득공제 항목입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    deduction("deduction.small-business-mutual-aid", "소기업·소상공인 공제부금", "노란우산 등 소기업·소상공인 공제부금에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.housing-savings", "주택마련저축", "청약저축, 주택청약종합저축, 근로자우대저축 등 주택마련저축 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.investment-association", "중소기업창업투자조합 출자 등", "중소기업창업투자조합 출자 등 투자 관련 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.credit-card-use", "신용카드 등 사용금액", "신용카드, 직불카드, 현금영수증 등 사용금액에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.credit-card-deduction", "source.nts.year-end-settlement.deduction-limit"], terms=["term.income-deduction", "term.deduction-limit", "term.eligibility-threshold"], criteria=CREDIT_CARD_DEDUCTION_CRITERIA),
    deduction("deduction.employee-stock-ownership", "우리사주조합 출연금", "우리사주조합 출연금 관련 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.employment-maintenance-worker", "고용유지중소기업 근로자 소득공제", "고용유지 중소기업 근로자에게 적용되는 소득공제 항목입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    deduction("deduction.long-term-fund", "장기집합투자증권저축", "장기집합투자증권저축에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.deduction-limit"]),
    deduction("deduction.youth-long-term-fund", "청년형 장기집합투자증권저축", "청년형 장기집합투자증권저축에 대한 소득공제입니다.", "deduction.other-income", sources=["source.nts.year-end-settlement.calculation"]),
    node("category.tax-credits", "세액공제", "category", "산출세액에서 직접 차감하는 공제 항목 묶음입니다.", "20_Deductions/TaxCredits", parents=["category.deductions-and-reliefs"], children=["credit.earned-income", "credit.child", "credit.pension-account", "credit.special-tax", "credit.monthly-rent", "credit.foreign-tax-paid", "credit.research-and-development", "credit.integrated-employment"], sources=["source.nts.year-end-settlement.calculation", "source.nts.year-end-settlement.special-credit", "source.nts.corporate-tax.reliefs"], terms=["term.tax-credit"]),
    credit("credit.earned-income", "근로소득 세액공제", "근로소득자의 산출세액에서 차감되는 세액공제입니다.", sources=["source.nts.year-end-settlement.calculation"]),
    credit("credit.child", "자녀 세액공제", "자녀 수 등 요건에 따라 산출세액에서 차감되는 세액공제입니다.", related=["support.child-tax-credit"], sources=["source.nts.year-end-settlement.calculation"]),
    credit("credit.pension-account", "연금계좌 세액공제", "연금저축, 퇴직연금계좌 납입액 등에 대한 세액공제입니다.", sources=["source.nts.year-end-settlement.calculation"], terms=["term.tax-credit", "term.eligibility-threshold"], criteria=PENSION_ACCOUNT_CREDIT_CRITERIA),
    node("credit.special-tax", "특별세액공제", "tax-credit", "근로소득자가 해당 과세기간에 지출한 일정 비용을 산출세액에서 공제하는 항목 묶음입니다.", "20_Deductions/TaxCredits", parents=["category.tax-credits"], children=["credit.insurance-premium", "credit.medical-expense", "credit.education-expense", "credit.donation"], sources=["source.nts.year-end-settlement.special-credit", "source.nts.education-expense-credit", "source.nts.donation-credit"], terms=["term.tax-credit"], criteria=SPECIAL_TAX_CREDIT_CRITERIA),
    credit("credit.insurance-premium", "보험료 세액공제", "보장성보험료, 장애인전용 보장성보험료 등에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.medical-expense", "의료비 세액공제", "총급여액의 일정 비율 초과 의료비 등에 대한 특별세액공제입니다.", "credit.special-tax", terms=["term.tax-credit", "term.eligibility-threshold"], criteria=MEDICAL_EXPENSE_CREDIT_CRITERIA),
    credit("credit.education-expense", "교육비 세액공제", "본인과 기본공제대상자 교육비 등에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.donation", "기부금 세액공제", "정치자금, 고향사랑, 특례, 우리사주조합, 일반기부금 등 공제한도 내 기부금에 대한 특별세액공제입니다.", "credit.special-tax"),
    credit("credit.monthly-rent", "월세액 세액공제", "무주택, 총급여·종합소득금액, 주택 요건 등을 충족한 월세액에 대한 세액공제입니다.", sources=["source.nts.monthly-rent-credit"], terms=["term.tax-credit", "term.eligibility-threshold"], criteria=MONTHLY_RENT_CREDIT_CRITERIA),
    credit("credit.foreign-tax-paid", "외국납부세액공제", "국외원천소득에 대한 이중과세 조정을 위한 세액공제입니다.", sources=["source.nts.corporate-tax.reliefs"]),
    credit("credit.research-and-development", "연구·인력개발비 세액공제", "일반, 신성장·원천기술, 국가전략기술 연구개발비 등에 대한 조세지원입니다.", sources=["source.nts.corporate-tax.reliefs"], related=["corporate.support.rnd-credit"]),
    credit("credit.integrated-employment", "통합고용세액공제", "고용 증가, 청년·장애인·경력단절자 등 정책 대상 고용에 대한 세액공제입니다.", sources=["source.nts.corporate-tax.reliefs"]),
    node("category.tax-reductions", "세액감면", "category", "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 감면 항목 묶음입니다.", "20_Deductions/TaxReductions", parents=["category.deductions-and-reliefs"], children=["reduction.sme-employment-income", "reduction.startup-sme", "reduction.sme-special", "reduction.good-landlord"], sources=["source.nts.year-end-settlement.calculation", "source.nts.corporate-tax.reliefs"], terms=["term.tax-reduction"]),
    node("reduction.sme-employment-income", "중소기업 취업자 소득세 감면", "tax-reduction", "청년 등 중소기업 취업자의 소득세를 일정 요건에서 감면하는 항목입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.sme-employment-income-reduction"], terms=["term.tax-reduction"], criteria=SME_EMPLOYMENT_INCOME_REDUCTION_CRITERIA),
    node("reduction.startup-sme", "창업중소기업 등에 대한 세액감면", "tax-reduction", "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 세액감면입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs", "source.nts.corporate-tax-consulting.2026"], terms=["term.tax-reduction"], related=["corporate.support.startup-sme-reduction"], criteria=STARTUP_SME_REDUCTION_CRITERIA),
    node("reduction.sme-special", "중소기업특별세액감면", "tax-reduction", "제조업 등 일정 업종 중소기업 소득에 대한 세액감면입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs", "source.nts.corporate-tax-consulting.2026"], terms=["term.tax-reduction"], related=["corporate.support.sme-special-reduction"], criteria=SME_SPECIAL_REDUCTION_CRITERIA),
    node("reduction.good-landlord", "착한임대인 세액공제 제도", "tax-reduction", "상가건물 임대료 인하액에 적용되는 세액공제 제도입니다.", "20_Deductions/TaxReductions", parents=["category.tax-reductions"], sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-credit", "term.tax-reduction"], related=["corporate.support.good-landlord-credit"], criteria=GOOD_LANDLORD_REDUCTION_CRITERIA),
    node("category.corporate-tax-supports", "법인세 공제·감면 지원제도", "category", "국세청 법인세 공제감면 안내가 열거한 중소기업, 모든 기업, 법인세법상 조세지원 항목 전체 목록입니다.", "20_Deductions/CorporateTaxSupports", parents=["category.deductions-and-reliefs"], children=CORPORATE_SUPPORT_IDS, sources=["source.nts.corporate-tax.reliefs"], terms=["term.tax-credit", "term.tax-reduction"], tags=["complete-manifest"]),
]


NODES.extend([
    corporate_support("corporate.support.startup-sme-reduction", "창업중소기업 등에 대한 세액감면", "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 법인세 조세지원입니다.", related=["reduction.startup-sme"]),
    corporate_support("corporate.support.sme-special-reduction", "중소기업특별세액감면", "제조업 등 일정 업종 중소기업 소득에 대한 법인세 감면입니다.", related=["reduction.sme-special"]),
    corporate_support("corporate.support.tech-transfer-reduction", "기술이전·대여 세액감면", "기술이전 및 기술취득 등에 대한 과세특례입니다."),
    corporate_support("corporate.support.winwin-payment-credit", "상생결제 지급금액 세액공제", "상생결제제도를 통해 구매대금을 지급한 경우 적용되는 세액공제입니다."),
    corporate_support("corporate.support.wage-increase-credit", "근로소득을 증대시킨 기업에 대한 세액공제", "임금 증가와 정규직 전환 근로자 임금 증가 등에 대한 세액공제입니다."),
    corporate_support("corporate.support.performance-sharing-credit", "성과공유 중소기업의 경영성과급 세액공제", "중소기업이 요건을 충족한 경영성과급을 지급하는 경우 적용되는 세액공제입니다."),
    corporate_support("corporate.support.employment-maintenance-credit", "고용유지 중소기업 등에 대한 과세특례", "임금 감소와 시간당 임금 보전액 등을 기준으로 적용되는 세액공제입니다."),
    corporate_support("corporate.support.social-insurance-credit", "사회보험료 세액공제", "고용증가인원의 사회보험료 상당액에 적용되는 세액공제입니다."),
    corporate_support("corporate.support.minimum-tax-preference", "최저한세 적용한도 우대", "중소기업 등에게 일반법인보다 우대되는 최저한세율을 적용하는 지원입니다."),
    corporate_support("corporate.support.cooperation-credit", "상생협력에 대한 조세지원", "협력중소기업 지원 목적 출연금과 유형고정자산 무상임대 등에 대한 조세지원입니다."),
    corporate_support("corporate.support.rnd-credit", "연구·인력개발비 세액공제", "일반, 신성장·원천기술, 국가전략기술 연구개발비에 대한 세액공제입니다.", related=["credit.research-and-development"]),
    corporate_support("corporate.support.rnd-grant-deferral", "연구개발 관련 출연금등의 과세이연", "연구개발출연금 등에 대한 익금불산입 지원입니다."),
    corporate_support("corporate.support.rnd-zone-reduction", "연구개발특구 입주 기업 감면", "첨단기술 및 연구소기업 등에 적용되는 법인세 감면입니다."),
    corporate_support("corporate.support.ma-credit", "M&A 활성화 지원", "기술혁신형 합병·주식취득 인수가액 중 기술가치 금액에 대한 법인세 공제입니다."),
    corporate_support("corporate.support.facility-investment-credit", "시설투자 등에 대한 세액공제", "각종 시설투자 금액과 투자 증가분에 적용되는 세액공제입니다."),
    corporate_support("corporate.support.local-relocation-reduction", "공장·본사 등 지방이전 세액감면", "수도권과밀억제권역 본사·공장 지방 이전 등에 적용되는 세액감면입니다."),
    corporate_support("corporate.support.agricultural-corporation-reduction", "영농조합법인 등에 대한 감면", "영농조합법인, 영어조합법인, 농업회사법인 등의 농어업소득 등에 대한 감면입니다."),
    corporate_support("corporate.support.industrial-complex-reduction", "농공단지 등 입주 기업 감면", "농공단지 등 입주 후 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 감면입니다."),
    corporate_support("corporate.support.social-enterprise-reduction", "사회적기업 등에 대한 감면", "사회적기업 인증 법인과 장애인 표준사업장 등에 적용되는 감면입니다."),
    corporate_support("corporate.support.jeju-zone-reduction", "제주첨단과학기술단지 등 입주 감면", "제주첨단과학기술단지 또는 제주투자진흥지구 입주기업 감면입니다."),
    corporate_support("corporate.support.enterprise-city-reduction", "기업도시개발구역 창업기업 등 감면", "기업도시개발구역 창업 또는 사업장 신설 기업에 적용되는 감면입니다."),
    corporate_support("corporate.support.e-filing-credit", "전자신고 세액공제", "법인이 직접 법인세를 전자신고할 때 적용되는 세액공제입니다."),
    corporate_support("corporate.support.restructuring-deferral", "구조조정 및 재무구조개선 과세이연", "양도차익 등에 대한 손금산입 또는 익금불산입 등 구조조정 지원입니다."),
    corporate_support("corporate.support.local-relocation-deferral", "지방이전 촉진 과세이연", "지방이전 등을 촉진하기 위한 양도차익 등의 손금산입 또는 익금불산입 지원입니다."),
    corporate_support("corporate.support.good-landlord-credit", "상가임대료 인하 임대사업자 세액공제", "상가건물 임대료 인하액에 적용되는 세액공제입니다.", related=["reduction.good-landlord"]),
    corporate_support("corporate.support.crisis-area-startup-reduction", "위기지역 창업기업 감면", "위기지역 지정 또는 선포 기간에 창업하거나 사업장을 신설한 기업에 대한 감면입니다."),
    corporate_support("corporate.support.disaster-loss-credit", "재해손실세액공제", "천재지변 등 재해로 사업용 총자산가액의 20% 이상을 상실한 경우 적용되는 법인세법상 세액공제입니다."),
    corporate_support("corporate.support.foreign-tax-paid-credit", "외국납부세액공제", "국외원천소득에 대한 이중과세 조정을 위한 법인세법상 세액공제입니다.", related=["credit.foreign-tax-paid"]),
    node("support.earned-income-tax-credit", "근로장려금", "support-program", "근로·사업·종교인소득이 있는 저소득 가구의 근로를 장려하기 위해 지급하는 국세청 지원금입니다. 2025년 귀속 소득 기준은 단독 2,200만원, 홑벌이 3,200만원, 맞벌이 4,400만원 미만입니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income.comprehensive"], terms=["term.total-income", "term.gross-pay", "term.property-requirement", "term.eligibility-threshold"], deadlines=["deadline.grant.regular.2025-income", "deadline.grant.semiannual.2026"], sources=["source.nts.eitc.intro", "source.nts.grant.eligibility", "source.nts.grant.deadline", "source.nts.grant.2026-regular-press"], basis_year=2025, tags=["cash-support"], criteria=EITC_CRITERIA),
    node("support.child-tax-credit", "자녀장려금", "support-program", "18세 미만 부양자녀가 있는 저소득 가구의 자녀양육을 지원하는 국세청 지원금입니다. 2025년 귀속 총소득 기준은 홑벌이·맞벌이 7,000만원 미만입니다.", "30_Supports", parents=["category.policy-supports"], related=["credit.child"], terms=["term.total-income", "term.property-requirement", "term.eligibility-threshold"], deadlines=["deadline.grant.regular.2025-income"], sources=["source.nts.ctc.intro", "source.nts.grant.eligibility", "source.nts.grant.deadline", "source.nts.grant.2026-regular-press"], basis_year=2025, tags=["cash-support"], criteria=CTC_CRITERIA),
    node("support.basic-livelihood-benefit", "생계급여", "support-program", "생활이 어려운 국민기초생활보장 수급자에게 최저생활 보장을 위해 현금 급여를 지급하는 정부24 복지급여입니다. 2026년 선정·급여기준은 기준 중위소득 32%입니다.", "30_Supports", parents=["category.policy-supports"], related=["support.illegal-private-finance-prevention-loan"], terms=["term.median-income", "term.eligibility-threshold"], sources=["source.govkr.basic-livelihood-benefit"], basis_year=2026, tags=["cash-support", "gov24", "welfare"], criteria=BASIC_LIVELIHOOD_BENEFIT_CRITERIA),
    node("support.youth-future-savings", "청년미래적금", "support-program", "2026년 6월 출시 예정인 청년 자산형성 정책형 적금입니다. 월 납입액에 대해 일반형과 우대형 정부기여금을 매칭하고 이자소득 비과세 특례를 연결합니다.", "30_Supports", parents=["category.policy-supports"], related=["support.youth-leap-account", "tax.income"], terms=["term.policy-finance", "term.median-income", "term.eligibility-threshold"], sources=["source.fsc.youth-future-savings"], basis_year=2026, tags=["asset-building", "policy-finance", "planned-2026"], criteria=YOUTH_FUTURE_SAVINGS_CRITERIA),
    node("support.youth-leap-account", "청년도약계좌", "support-program", "청년의 중장기 자산형성을 지원하는 정책금융 상품입니다. 세금 세목은 아니지만 소득 요건, 금융소득종합과세 이력 제한, 비과세·정부기여금 학습 항목으로 연결합니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income"], terms=["term.total-income", "term.eligibility-threshold"], sources=["source.kinfa.youth-leap"], tags=["policy-finance"], criteria=YOUTH_LEAP_CRITERIA),
    node("support.isa", "개인종합자산관리계좌 ISA", "support-program", "개인이 예·적금, 펀드, 파생결합증권 등을 한 계좌에서 운용하며 세제혜택을 받을 수 있는 정책성 금융계좌입니다.", "30_Supports", parents=["category.policy-supports"], related=["tax.income"], sources=["source.fsc.isa.policy"], terms=["term.tax-credit"], tags=["policy-finance", "tax-preferred-account"]),
    node("support.illegal-private-finance-prevention-loan", "불법사금융예방대출", "support-program", "대부업조차 이용이 어려운 저신용·저소득자의 생계비를 지원해 불법사금융 피해를 예방하는 서민금융진흥원 정책서민금융상품입니다.", "30_Supports", parents=["category.policy-supports"], related=["support.basic-livelihood-benefit"], terms=["term.policy-finance", "term.policy-loan", "term.eligibility-threshold"], sources=["source.kinfa.illegal-private-finance-prevention-loan"], basis_year=2026, tags=["policy-finance", "loan", "vulnerable-finance"], criteria=ILLEGAL_PRIVATE_FINANCE_PREVENTION_LOAN_CRITERIA),
    node("support.hessal-loan-youth", "햇살론유스", "support-program", "대학생, 미취업청년, 사회초년생, 저소득 청년 개인사업자의 학업·취업준비·사회진입 자금을 보증 지원하는 서민금융진흥원 정책대출입니다.", "30_Supports", parents=["category.policy-supports"], related=["support.youth-future-savings", "support.youth-leap-account"], terms=["term.policy-finance", "term.policy-loan", "term.eligibility-threshold"], sources=["source.kinfa.hessal-loan-youth"], basis_year=2026, tags=["policy-finance", "loan", "youth"], criteria=HESSAL_LOAN_YOUTH_CRITERIA),
    node("support.hessal-119", "햇살론119", "support-program", "은행권 채무조정 프로그램을 성실상환 중인 연 매출 3억원 이하 영세 개인사업자에게 사업 운영 신규 운전자금을 보증부 대출로 지원하는 상품입니다.", "30_Supports", parents=["category.policy-supports"], related=["category.business-tax-compliance", "support.long-term-delinquent-debt-adjustment"], terms=["term.policy-finance", "term.policy-loan", "term.debt-adjustment", "term.eligibility-threshold"], sources=["source.kinfa.hessal-119"], basis_year=2026, tags=["policy-finance", "loan", "small-business"], criteria=HESSAL_119_CRITERIA),
    node("support.didimdol-loan", "내집마련 디딤돌대출", "support-program", "무주택 서민의 주택 구입자금을 낮은 금리로 공급하는 정책모기지입니다. 소득, 순자산, 주택가격, LTV·DTI, 대출한도를 함께 확인합니다.", "30_Supports", parents=["category.policy-supports"], related=["credit.monthly-rent", "tax.comprehensive-real-estate"], terms=["term.policy-finance", "term.policy-loan", "term.eligibility-threshold"], sources=["source.hf.didimdol-loan", "source.hf.didimdol-rate.2026-05"], basis_year=2026, tags=["policy-finance", "housing", "loan"], criteria=DIDIMDOL_LOAN_CRITERIA),
    node("support.youth-special-rent-guarantee", "무주택 청년 특례전세자금보증", "support-program", "무주택 청년 등 주거취약 대상에게 일반전세자금보증보다 완화된 요건과 보증한도를 적용하는 한국주택금융공사 특례보증입니다.", "30_Supports", parents=["category.policy-supports"], related=["support.didimdol-loan", "credit.monthly-rent"], terms=["term.policy-finance", "term.policy-loan", "term.eligibility-threshold"], sources=["source.hf.special-rent-guarantee"], basis_year=2026, tags=["policy-finance", "housing", "guarantee", "youth"], criteria=YOUTH_SPECIAL_RENT_GUARANTEE_CRITERIA),
    node("support.long-term-delinquent-debt-adjustment", "장기연체자 특별채무조정", "support-program", "새도약기금 관련 장기연체채권 중 상환능력이 있는 채무자를 대상으로 신용회복위원회가 이자 감면, 원금감면, 분할상환, 상환유예를 지원하는 채무조정 제도입니다.", "30_Supports", parents=["category.policy-supports"], related=["support.hessal-119"], terms=["term.debt-adjustment", "term.median-income", "term.eligibility-threshold"], sources=["source.ccrs.long-term-delinquent-debt-adjustment"], basis_year=2026, tags=["debt-adjustment", "policy-finance", "vulnerable-finance"], criteria=LONG_TERM_DELINQUENT_DEBT_ADJUSTMENT_CRITERIA),
    node("filing.income-tax-return", "종합소득세 확정신고", "filing", "종합소득이 있는 개인이 다음연도 5월 신고·납부하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["tax.income.comprehensive"], terms=["term.deadline", "term.deadline-special-rule"], deadlines=["deadline.income-tax.2025-return"], sources=["source.nts.income-tax.deadline"], basis_year=2025),
    node("filing.year-end-settlement", "연말정산", "filing", "원천징수의무자가 근로자의 해당 과세기간 근로소득세를 확정하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["category.deductions-and-reliefs"], terms=["term.withholding", "term.income-deduction", "term.tax-credit"], deadlines=["deadline.year-end-settlement"], sources=["source.nts.year-end-settlement.calculation"]),
    node("filing.business-registration", "사업자등록 신청", "filing", "신규사업자가 사업 개시 전 또는 사업 개시일부터 20일 이내 관할 세무서장에게 등록하는 절차입니다. 일반과세자·간이과세자 유형 선택과 간이과세 배제 업종 확인을 함께 관리합니다.", "60_Business", parents=["category.business-tax-compliance"], related=["tax.value-added", "concept.general-vat-taxpayer", "concept.simple-vat-taxpayer"], terms=["term.general-vat-taxpayer", "term.simple-vat-taxpayer"], sources=["source.nts.business-registration.application"], tags=["business-compliance"]),
    node("filing.withholding-tax", "원천세 신고 납부 절차", "filing", "원천징수의무자가 원천징수한 세액을 신고·납부하는 절차입니다. 매월 납부와 반기별 납부를 모두 연결해 급여·사업소득 지급자의 반복 업무로 관리합니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["filing.business-income-withholding"], terms=["term.withholding", "term.withholding-obligor", "term.deadline-special-rule"], deadlines=["deadline.withholding.monthly", "deadline.withholding.semiannual"], sources=["source.nts.tax-calendar.2026", "source.nts.withholding.overview", "source.nts.business-income.withholding"]),
    node("filing.business-income-withholding", "사업소득 원천징수", "filing", "프리랜서 등 원천징수 대상 사업소득을 지급할 때 지급금액의 일정 비율을 원천징수하고 정해진 기한에 신고·납부하는 흐름입니다.", "60_Business", parents=["category.business-tax-compliance", "filing.withholding-tax"], related=["tax.income.comprehensive"], terms=["term.withholding", "term.withholding-obligor", "term.tax-rate", "term.deadline-special-rule"], deadlines=["deadline.withholding.monthly", "deadline.withholding.semiannual"], sources=["source.nts.business-income.withholding", "source.nts.withholding.overview"], tags=["business-compliance"], criteria=BUSINESS_INCOME_WITHHOLDING_CRITERIA),
    node("filing.vat-return", "부가가치세 신고 납부 절차", "filing", "부가가치세 과세사업자가 과세기간별 매출세액과 매입세액을 신고·납부하는 절차입니다. 일반과세자 확정신고, 간이과세자 연간 신고, 일부 간이과세자 예정신고 예외를 함께 관리합니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["tax.value-added", "concept.general-vat-taxpayer", "concept.simple-vat-taxpayer", "concept.vat-payment-exemption", "filing.business-registration"], terms=["term.tax-period", "term.general-vat-taxpayer", "term.simple-vat-taxpayer", "term.deadline-special-rule"], deadlines=["deadline.vat.periodic", "deadline.vat.general.first-final", "deadline.vat.general.second-final", "deadline.vat.simplified.annual", "deadline.vat.simplified.preliminary"], sources=["source.nts.vat.overview", "source.nts.vat.filing-duty", "source.nts.tax-calendar.2026"]),
    node("filing.capital-gains-return", "양도소득세 신고", "filing", "부동산, 주식 등 자산 양도 후 예정신고와 다음연도 확정신고 필요 여부를 구분해 관리하는 신고 절차입니다.", "50_Deadlines", parents=["category.filing-calendar", "tax.income.capital-gains"], related=["tax.securities-transaction"], terms=["term.capital-gain", "term.tax-base", "term.deadline"], deadlines=["deadline.capital-gains.preliminary", "deadline.capital-gains.final"], sources=["source.nts.capital-gains.overview", "source.nts.capital-gains.deadline"]),
    node("filing.inheritance-tax-return", "상속세 신고", "filing", "상속개시일이 속하는 달의 말일부터 거주자 6개월, 비거주자 9개월 기한을 기준으로 신고·납부를 관리하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar", "tax.inheritance"], terms=["term.heir", "term.tax-base", "term.deadline"], deadlines=["deadline.inheritance.resident", "deadline.inheritance.nonresident"], sources=["source.nts.inheritance.overview"]),
    node("filing.gift-tax-return", "증여세 신고", "filing", "증여받은 날이 속하는 달의 말일부터 일반 증여 3개월 기한을 기준으로 신고·납부를 관리하는 절차입니다.", "50_Deadlines", parents=["category.filing-calendar", "tax.gift"], terms=["term.donee", "term.tax-base", "term.deadline"], deadlines=["deadline.gift.general"], sources=["source.nts.gift.deadline"]),
    node("filing.grant-application", "근로·자녀장려금 신청", "filing", "국세청 근로·자녀장려금 정기·반기·기한 후 신청 및 심사 흐름입니다.", "50_Deadlines", parents=["category.filing-calendar"], related=["support.earned-income-tax-credit", "support.child-tax-credit"], terms=["term.total-income", "term.property-requirement"], deadlines=["deadline.grant.regular.2025-income", "deadline.grant.semiannual.2026"], sources=["source.nts.grant.eligibility", "source.nts.grant.deadline"], basis_year=2025),
    node("concept.general-vat-taxpayer", "일반과세자 기준", "concept", "부가가치세에서 일반 세율과 매입세액 공제 구조를 적용받는 과세사업자 유형입니다. 사업자등록과 부가가치세 신고 시 간이과세자 기준과 함께 확인합니다.", "40_Terms/Concepts", parents=["tax.value-added"], related=["concept.simple-vat-taxpayer", "filing.business-registration", "filing.vat-return"], terms=["term.general-vat-taxpayer", "term.tax-rate", "term.eligibility-threshold"], sources=["source.nts.vat.overview", "source.nts.vat.filing-duty", "source.nts.business-registration.application"], criteria=[VAT_CRITERIA[0], VAT_CRITERIA[2]]),
    node("concept.simple-vat-taxpayer", "간이과세자 기준", "concept", "부가가치세에서 1년 매출액 10,400만원 미만 개인사업자에게 적용되는 납세 유형 기준입니다. 사업자등록 단계에서 간이과세 배제 업종과 일반과세자 전환 가능성을 함께 확인합니다.", "40_Terms/Concepts", parents=["tax.value-added"], related=["concept.general-vat-taxpayer", "concept.vat-payment-exemption", "filing.business-registration", "filing.vat-return"], terms=["term.simple-vat-taxpayer", "term.tax-rate", "term.eligibility-threshold"], deadlines=["deadline.vat.simplified.annual", "deadline.vat.simplified.preliminary"], sources=["source.nts.vat.overview", "source.nts.vat.filing-duty", "source.nts.business-registration.application"], criteria=[VAT_CRITERIA[1], VAT_CRITERIA[3], VAT_CRITERIA[4], VAT_CRITERIA[5]]),
    node("concept.vat-payment-exemption", "간이과세자 납부의무 면제", "concept", "직전연도 공급대가가 일정 금액 미만인 간이과세자는 부가가치세 납부세액의 납부의무가 면제될 수 있어 신고와 납부 판단을 분리해 확인해야 합니다.", "40_Terms/Concepts", parents=["tax.value-added"], related=["concept.simple-vat-taxpayer", "filing.vat-return"], terms=["term.simple-vat-taxpayer", "term.eligibility-threshold"], sources=["source.nts.vat.filing-duty"], criteria=[VAT_CRITERIA[5]]),
    node("concept.capital-gains.calculation-flow", "양도소득세 계산 흐름", "concept", "양도가액, 취득가액, 필요경비, 장기보유특별공제, 기본공제 등을 거쳐 양도소득 과세표준과 산출세액을 파악하는 계산 구조입니다.", "10_Taxes/National/CapitalGains", parents=["tax.income.capital-gains"], related=["filing.capital-gains-return"], terms=["term.capital-gain", "term.tax-base"], sources=["source.nts.capital-gains.overview"]),
    node("concept.capital-gains.stock-basic-deduction", "주식 등 양도소득 기본공제", "concept", "주식 등 양도소득은 국내·국외주식 등 그룹별 기본공제 적용 여부를 확인해야 하며, 증권거래세와 별도로 양도차익 과세 흐름을 관리합니다.", "10_Taxes/National/CapitalGains", parents=["tax.income.capital-gains"], related=["tax.securities-transaction", "filing.capital-gains-return"], terms=["term.capital-gain"], sources=["source.nts.capital-gains.overview"]),
    node("concept.cre-tax-base-date", "종합부동산세 과세기준일", "concept", "종합부동산세는 매년 6월 1일 현재 보유한 주택과 토지를 기준으로 재산세 과세자료와 연결해 과세대상을 판단합니다.", "10_Taxes/National/RealEstate", parents=["tax.comprehensive-real-estate"], related=["local.property"], terms=["term.publicly-notified-price"], sources=["source.nts.comprehensive-real-estate.overview"]),
    node("concept.cre-deduction-thresholds", "종합부동산세 공제금액", "concept", "종합부동산세는 주택, 종합합산토지, 별도합산토지 등 과세대상별 공제금액을 먼저 차감한 뒤 과세표준을 계산합니다.", "10_Taxes/National/RealEstate", parents=["tax.comprehensive-real-estate"], related=["local.property"], terms=["term.publicly-notified-price", "term.tax-base", "term.eligibility-threshold"], sources=["source.nts.comprehensive-real-estate.overview"], criteria=CRE_CRITERIA[:4]),
])


def title_by_id(all_items: dict[str, dict], id_: str) -> str:
    return all_items[id_]["title"]


def obsidian_link(all_items: dict[str, dict], id_: str) -> str:
    item = all_items[id_]
    target = f"{item['folder']}/{slug(item['title'])}"
    return f"[[{target}|{item['title']}]]"


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def normalize_graph(nodes: list[dict]) -> None:
    by_id = {item["id"]: item for item in nodes}
    for item in nodes:
        for child_id in list(item["children"]):
            if child_id in by_id and item["id"] not in by_id[child_id]["parents"]:
                by_id[child_id]["parents"].append(item["id"])
        for parent_id in list(item["parents"]):
            if parent_id in by_id and item["id"] not in by_id[parent_id]["children"]:
                by_id[parent_id]["children"].append(item["id"])
        for related_id in list(item["related"]):
            if related_id in by_id and item["id"] not in by_id[related_id]["related"]:
                by_id[related_id]["related"].append(item["id"])
    for item in nodes:
        for key in ("parents", "children", "related", "terms", "deadlines", "sources", "tags"):
            item[key] = unique(item[key])


def normalize_items(items: dict[str, dict]) -> None:
    for item in items.values():
        for child_id in list(item.get("children") or []):
            child = items.get(child_id)
            if child and item["id"] not in (child.get("parents") or []):
                child.setdefault("parents", []).append(item["id"])
        for parent_id in list(item.get("parents") or []):
            parent = items.get(parent_id)
            if parent and item["id"] not in (parent.get("children") or []):
                parent.setdefault("children", []).append(item["id"])
        for related_id in list(item.get("related") or []):
            related = items.get(related_id)
            if related and item["id"] not in (related.get("related") or []):
                related.setdefault("related", []).append(item["id"])

    for item in items.values():
        attach_default_criteria(item)
        for key in ("parents", "children", "related", "terms", "deadlines", "sources", "tags"):
            item[key] = unique(item.get(key) or [])
        normalize_criteria_rate_labels(item)
        add_missing_amount_metadata(item)


def default_criteria_rate_label(item: dict) -> str | None:
    item_type = item.get("type")
    if item_type == "deduction":
        return "소득공제율"
    if item_type == "tax-credit":
        return "세액공제율"
    if item_type == "tax-reduction":
        return "감면율"
    if item_type == "corporate-tax-support":
        return "공제·감면율"
    return None


def normalize_criteria_rate_labels(item: dict) -> None:
    label = default_criteria_rate_label(item)
    if not label:
        return
    for criterion in item.get("criteria") or []:
        if criterion.get("rate_label"):
            continue
        if any(key in criterion for key in ("rate_percent", "rate_percent_min", "rate_percent_max")):
            criterion["rate_label"] = label


AMOUNT_DETAIL_KEYS = {
    "threshold_krw",
    "threshold_krw_min",
    "threshold_krw_max",
    "amount_krw",
    "max_amount_krw",
    "deduction_krw",
    "limit_krw",
    "progressive_deduction_krw",
    "amount_formula",
    "amount_applicability",
}


def attach_default_criteria(item: dict) -> None:
    if item.get("criteria"):
        return
    criteria = globals().get("ITEM_CRITERIA_BY_ID", {}).get(item["id"])
    if not criteria:
        return
    item["criteria"] = criteria
    for criterion in criteria:
        source_id = criterion.get("source")
        if source_id and source_id not in item.get("sources", []):
            item.setdefault("sources", []).append(source_id)


def criterion_has_amount_detail(criterion: dict) -> bool:
    return any(key in criterion for key in AMOUNT_DETAIL_KEYS)


def rate_text(criterion: dict) -> str | None:
    if "rate_percent" in criterion:
        return f"{criterion['rate_percent']}%"
    if "rate_percent_min" in criterion and "rate_percent_max" in criterion:
        return f"{criterion['rate_percent_min']}%~{criterion['rate_percent_max']}%"
    if "rate_percent_min" in criterion:
        return f"{criterion['rate_percent_min']}% 이상"
    if "rate_percent_max" in criterion:
        return f"{criterion['rate_percent_max']}% 이하"
    return None


def add_missing_amount_metadata(item: dict) -> None:
    for criterion in item.get("criteria") or []:
        if criterion_has_amount_detail(criterion):
            continue
        rate = rate_text(criterion)
        basis = criterion.get("basis") or criterion.get("label") or "기준금액"
        if rate:
            rate_label = criterion.get("rate_label") or default_criteria_rate_label(item) or "적용비율"
            if rate_label in {"금리", "보증료율", "LTV", "DTI"}:
                criterion["amount_applicability"] = RATE_ONLY_AMOUNT
            else:
                criterion["amount_formula"] = f"{basis} × {rate_label} {rate}"
        elif "전액" in (criterion.get("benefit") or ""):
            criterion["amount_formula"] = f"{basis} 전액"
        else:
            criterion["amount_applicability"] = NO_FIXED_AMOUNT


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for key in [
        "id",
        "title",
        "type",
        "description",
        "basis_year",
        "effective_date",
        "expiration_date",
        "parents",
        "children",
        "related",
        "terms",
        "deadlines",
        "sources",
        "criteria",
        "law_reference",
        "tags",
        "publisher",
        "url",
        "basis_date",
        "start_date",
        "end_date",
    ]:
        value = fields.get(key)
        if value is not None:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def slug(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', " ", title).strip()


def render_criteria(item: dict, all_items: dict[str, dict]) -> list[str]:
    criteria = item.get("criteria") or []
    if not criteria:
        return []

    labels = {
        "label": "기준",
        "basis": "기준항목",
        "condition": "조건",
        "rate_percent": "세율",
        "rate_percent_min": "최저세율",
        "rate_percent_max": "최고세율",
        "progressive_deduction_krw": "누진공제",
        "threshold_krw": "기준금액",
        "threshold_krw_min": "하한",
        "threshold_krw_max": "상한",
        "amount_krw": "금액",
        "amount_formula": "금액·적용 산식",
        "amount_applicability": "금액 기준 여부",
        "max_amount_krw": "최대금액",
        "deduction_krw": "공제액",
        "limit_krw": "한도",
        "benefit": "혜택",
        "note": "비고",
    }
    order = [
        "basis",
        "condition",
        "amount_applicability",
        "threshold_krw_min",
        "threshold_krw",
        "threshold_krw_max",
        "rate_percent",
        "rate_percent_min",
        "rate_percent_max",
        "progressive_deduction_krw",
        "deduction_krw",
        "limit_krw",
        "amount_krw",
        "amount_formula",
        "max_amount_krw",
        "benefit",
        "note",
    ]

    body = ["## 기준 내역", ""]
    for criterion in criteria:
        title = criterion.get("label", "기준")
        pieces: list[str] = []
        for key in order:
            value = criterion.get(key)
            if value is None or value == "":
                continue
            if key.endswith("_krw") or key in {"threshold_krw_min", "threshold_krw_max"}:
                value = f"{int(value):,}원"
            elif key.startswith("rate_percent"):
                value = f"{value}%"
            if key.startswith("rate_percent"):
                rate_label = criterion.get("rate_label")
                if rate_label and key == "rate_percent_min":
                    label = f"최저{rate_label}"
                elif rate_label and key == "rate_percent_max":
                    label = f"최고{rate_label}"
                else:
                    label = rate_label or labels[key]
            else:
                label = labels[key]
            pieces.append(f"{label}: {value}")
        source_id = criterion.get("source")
        if source_id in all_items:
            pieces.append(f"출처: {obsidian_link(all_items, source_id)}")
        body.append(f"- **{title}**: " + "; ".join(pieces))
    body.append("")
    return body


def render_note(item: dict, all_items: dict[str, dict]) -> str:
    body = [frontmatter(item), "", f"# {item['title']}", "", item["description"], ""]
    if item.get("law_reference"):
        body.extend(["## 근거 조항", "", item["law_reference"], ""])
    body.extend(render_criteria(item, all_items))
    for heading, key in [
        ("상위 항목", "parents"),
        ("하위 항목", "children"),
        ("관련 항목", "related"),
        ("관련 용어", "terms"),
        ("기한", "deadlines"),
        ("근거·출처", "sources"),
    ]:
        values = item.get(key, [])
        if values:
            body.extend([f"## {heading}", ""])
            for value in values:
                if key == "sources":
                    url = all_items[value].get("url")
                    if url:
                        body.append(f"- {obsidian_link(all_items, value)}: {url}")
                    else:
                        body.append(f"- {obsidian_link(all_items, value)}")
                else:
                    body.append(f"- {obsidian_link(all_items, value)}")
            body.append("")
    body.extend(["## 온톨로지 ID", "", f"`{item['id']}`", ""])
    return "\n".join(body)


def render_source(source_id: str, source: dict) -> dict:
    return {
        "id": source_id,
        "title": source["title"],
        "type": "source",
        "description": source["description"],
        "folder": "90_Sources",
        "basis_year": None,
        "effective_date": None,
        "expiration_date": None,
        "parents": [],
        "children": [],
        "related": [],
        "terms": [],
        "deadlines": [],
        "sources": [],
        "law_reference": "",
        "tags": ["official-source", source["publisher"]],
        "publisher": source["publisher"],
        "url": source["url"],
        "basis_date": source["basis_date"],
    }


def render_source_note(item: dict) -> str:
    fields = {key: item.get(key) for key in [
        "id", "title", "type", "description", "basis_year", "effective_date", "expiration_date",
        "parents", "children", "related", "terms", "deadlines", "sources", "law_reference",
        "tags", "publisher", "url", "basis_date"
    ]}
    body = [
        frontmatter(fields),
        "",
        f"# {item['title']}",
        "",
        item["description"],
        "",
        "## 발행기관",
        "",
        item["publisher"],
        "",
        "## 기준일",
        "",
        item["basis_date"],
        "",
        "## 링크",
        "",
        item["url"],
        "",
        "## 온톨로지 ID",
        "",
        f"`{item['id']}`",
        "",
    ]
    return "\n".join(body)


def default_item_fields(item: dict) -> dict:
    result = {
        "basis_year": item.get("basis_year"),
        "effective_date": item.get("effective_date"),
        "expiration_date": item.get("expiration_date"),
        "parents": item.get("parents") or [],
        "children": item.get("children") or [],
        "related": item.get("related") or [],
        "terms": item.get("terms") or [],
        "deadlines": item.get("deadlines") or [],
        "sources": item.get("sources") or [],
        "law_reference": item.get("law_reference") or "",
        "tags": item.get("tags") or [],
    }
    if item.get("criteria"):
        result["criteria"] = item["criteria"]
    return {**item, **result}


def load_custom_items() -> list[dict]:
    if not CUSTOM_ITEMS_PATH.exists():
        return []

    payload = json.loads(CUSTOM_ITEMS_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = payload.get("items", [])
    if not isinstance(raw_items, list):
        raise ValueError(f"{CUSTOM_ITEMS_PATH} must contain an items array")
    return [dict(item) for item in raw_items]


def build_all_items() -> dict[str, dict]:
    nodes = [dict(item) for item in NODES]
    normalize_graph(nodes)

    items: dict[str, dict] = {item["id"]: item for item in nodes}
    for term_id, (title, description, sources) in TERMS.items():
        items[term_id] = node(
            term_id,
            title,
            "term",
            description,
            "40_Terms",
            basis_year=2026,
            sources=sources,
            tags=["term"],
        )
    for deadline_id, deadline in DEADLINES.items():
        items[deadline_id] = node(
            deadline_id,
            deadline["title"],
            "deadline",
            deadline["description"],
            "50_Deadlines",
            basis_year=deadline["basis_year"],
            sources=deadline["sources"],
            tags=["deadline"],
        )
        items[deadline_id]["start_date"] = deadline["start_date"]
        items[deadline_id]["end_date"] = deadline["end_date"]
    for source_id, source in SOURCES.items():
        items[source_id] = render_source(source_id, source)
    for custom_item in load_custom_items():
        item_id = custom_item["id"]
        if item_id in items:
            merged = {**items[item_id], **custom_item}
            merged["tags"] = unique((items[item_id].get("tags") or []) + (custom_item.get("tags") or []) + ["custom-overlay"])
            items[item_id] = default_item_fields(merged)
        else:
            custom_item["tags"] = unique((custom_item.get("tags") or []) + ["custom-overlay"])
            items[item_id] = default_item_fields(custom_item)
    normalize_items(items)
    return items


def expected_note_path(item: dict) -> Path:
    return VAULT / item["folder"] / f"{slug(item['title'])}.md"


def generated_note_id(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    if not text.startswith("---\n"):
        return None
    try:
        _, frontmatter_text, _ = text.split("---", 2)
    except ValueError:
        return None
    for raw_line in frontmatter_text.strip().splitlines():
        if raw_line.startswith("id: "):
            return json.loads(raw_line.split(": ", 1)[1])
    return None


def is_custom_overlay_note(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if not text.startswith("---\n"):
        return False
    try:
        _, frontmatter_text, _ = text.split("---", 2)
    except ValueError:
        return False
    return "custom-overlay" in frontmatter_text


def remove_stale_generated_notes(items: dict[str, dict]) -> None:
    expected_paths = {expected_note_path(item).resolve() for item in items.values()}
    item_ids = set(items)
    for path in VAULT.rglob("*.md"):
        note_id = generated_note_id(path)
        if note_id in item_ids and path.resolve() not in expected_paths:
            path.unlink()
        elif note_id not in item_ids and is_custom_overlay_note(path):
            path.unlink()


def write_markdown(items: dict[str, dict]) -> None:
    VAULT.mkdir(parents=True, exist_ok=True)
    remove_stale_generated_notes(items)
    for item in items.values():
        path = expected_note_path(item)
        path.parent.mkdir(parents=True, exist_ok=True)
        if item["type"] == "source":
            text = render_source_note(item)
        else:
            text = render_note(item, items)
        path.write_text(text, encoding="utf-8")


def write_index(items: dict[str, dict]) -> None:
    root = items["kr-tax-system"]
    index = expected_note_path(root)
    index.write_text(render_note(root, items), encoding="utf-8")


def write_export(items: dict[str, dict]) -> None:
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    export = {
        "version": "KR-TAX-OBSIDIAN-ONTOLOGY-2026.05.02",
        "basis_date": "2026-05-02",
        "manifests": {
            "national_tax_ids": NATIONAL_TAX_IDS,
            "local_tax_ids": LOCAL_TAX_IDS,
            "corporate_support_ids": CORPORATE_SUPPORT_IDS,
        },
        "items": sorted(items.values(), key=lambda item: item["id"]),
    }
    EXPORT_PATH.write_text(json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    items = build_all_items()
    write_markdown(items)
    write_index(items)
    write_export(items)
    print(f"Generated {len(items)} ontology notes into {VAULT}")
    print(f"Exported {EXPORT_PATH}")


if __name__ == "__main__":
    main()
