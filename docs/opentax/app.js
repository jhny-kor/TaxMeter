const ONTOLOGY_DATA = {
  "version": "KR-TAX-OBSIDIAN-ONTOLOGY-2026.05.02",
  "basis_date": "2026-05-02",
  "manifests": {
    "national_tax_ids": [
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
      "tax.special-rural-development"
    ],
    "local_tax_ids": [
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
      "local.local-education"
    ],
    "corporate_support_ids": [
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
      "corporate.support.foreign-tax-paid-credit"
    ]
  },
  "summary": {
    "item_count": 242,
    "source_count": 63,
    "term_count": 30,
    "category_count": 13,
    "deadline_count": 16,
    "support_count": 12,
    "business_count": 4,
    "relation_count": 1000,
    "national_tax_count": 12,
    "local_tax_count": 11,
    "corporate_support_count": 28,
    "type_counts": {
      "category": 13,
      "concept": 7,
      "corporate-tax-support": 28,
      "deadline": 16,
      "deduction": 17,
      "domain": 1,
      "filing": 10,
      "source": 63,
      "support-program": 12,
      "tax": 29,
      "tax-credit": 12,
      "tax-reduction": 4,
      "term": 30
    }
  },
  "type_labels": {
    "domain": "도메인",
    "category": "카테고리",
    "tax": "세목",
    "deduction": "소득공제",
    "tax-credit": "세액공제",
    "tax-reduction": "세액감면",
    "corporate-tax-support": "법인세 지원",
    "support-program": "정책지원",
    "filing": "신고 절차",
    "concept": "판정 개념",
    "term": "용어",
    "deadline": "기한",
    "source": "공식 출처"
  },
  "type_roles": {
    "domain": "최상위 지식 그래프 루트",
    "category": "세목·공제·지원·사업자 세무·기한의 탐색 축",
    "tax": "국세, 지방세, 관세 세목",
    "deduction": "과세표준 전 단계의 소득공제 항목",
    "tax-credit": "산출세액에서 차감하는 세액공제",
    "tax-reduction": "정책 목적의 세액감면",
    "corporate-tax-support": "법인세 공제·감면 공식 지원제도",
    "support-program": "장려금, 세제지원 계좌, 금융·복지 지원",
    "filing": "신고·납부·신청 절차",
    "concept": "판정 기준을 설명하는 개념 노드",
    "term": "그래프 해석에 필요한 용어",
    "deadline": "기준연도별 신고·납부·지급 기한",
    "source": "법률·기관별 공식 근거 URL"
  },
  "items": [
    {
      "id": "category.business-tax-compliance",
      "title": "사업자 세무",
      "type": "category",
      "description": "개인사업자와 원천징수의무자가 사업자등록, 부가가치세, 원천세 신고·납부에서 확인해야 하는 실무 흐름입니다.",
      "folder": "60_Business",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "filing.business-registration",
        "filing.vat-return",
        "filing.withholding-tax",
        "filing.business-income-withholding"
      ],
      "related": [
        "tax.value-added",
        "support.hessal-119"
      ],
      "terms": [
        "term.general-vat-taxpayer",
        "term.simple-vat-taxpayer",
        "term.withholding-obligor"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.business-registration.application",
        "source.nts.vat.filing-duty",
        "source.nts.withholding.overview",
        "source.nts.business-income.withholding"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.corporate-tax-supports",
      "title": "법인세 공제·감면 지원제도",
      "type": "category",
      "description": "국세청 법인세 공제감면 안내가 열거한 중소기업, 모든 기업, 법인세법상 조세지원 항목 전체 목록입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.deductions-and-reliefs"
      ],
      "children": [
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
        "corporate.support.foreign-tax-paid-credit"
      ],
      "related": [
        "tax.corporate"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "complete-manifest"
      ]
    },
    {
      "id": "category.customs",
      "title": "관세 영역",
      "type": "category",
      "description": "국세기본법 제2조의 국세 열거와 별개로 관세법에 근거해 수입물품에 부과되는 조세 영역입니다.",
      "folder": "10_Taxes/Customs",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "tax.customs"
      ],
      "related": [],
      "terms": [
        "term.customs"
      ],
      "deadlines": [],
      "sources": [
        "source.customs-act.2026.article14"
      ],
      "law_reference": "관세법 제14조",
      "tags": []
    },
    {
      "id": "category.deductions-and-reliefs",
      "title": "공제·감면",
      "type": "category",
      "description": "과세표준을 줄이는 소득공제, 산출세액에서 차감하는 세액공제, 정책 목적의 세액감면과 법인세 조세지원 항목입니다.",
      "folder": "20_Deductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "category.income-deductions",
        "category.tax-credits",
        "category.tax-reductions",
        "category.corporate-tax-supports"
      ],
      "related": [
        "filing.year-end-settlement"
      ],
      "terms": [
        "term.income-deduction",
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.filing-calendar",
      "title": "신고·납부·신청 기한",
      "type": "category",
      "description": "세목과 지원제도에 연결되는 기준연도별 기한입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "filing.income-tax-return",
        "filing.year-end-settlement",
        "filing.withholding-tax",
        "filing.vat-return",
        "filing.capital-gains-return",
        "filing.inheritance-tax-return",
        "filing.gift-tax-return",
        "filing.grant-application"
      ],
      "related": [],
      "terms": [
        "term.deadline",
        "term.deadline-special-rule"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.income-tax.deadline",
        "source.nts.tax-calendar.2026",
        "source.nts.grant.deadline",
        "source.nts.capital-gains.deadline",
        "source.nts.inheritance.overview",
        "source.nts.gift.deadline"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.income-deductions",
      "title": "소득공제",
      "type": "category",
      "description": "근로소득 연말정산에서 과세표준 전 단계에 반영되는 공제 묶음입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.deductions-and-reliefs"
      ],
      "children": [
        "deduction.personal",
        "deduction.pension-insurance",
        "deduction.special-income",
        "deduction.other-income"
      ],
      "related": [
        "tax.income"
      ],
      "terms": [
        "term.income-deduction",
        "term.deduction-limit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.local-ordinary-taxes",
      "title": "지방 보통세",
      "type": "category",
      "description": "지방세 중 특정 목적세가 아닌 보통세 세목 묶음입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.local-taxes"
      ],
      "children": [
        "local.acquisition",
        "local.registration-license",
        "local.leisure",
        "local.tobacco-consumption",
        "local.local-consumption",
        "local.resident",
        "local.local-income",
        "local.property",
        "local.automobile"
      ],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.local-purpose-taxes",
      "title": "지방 목적세",
      "type": "category",
      "description": "지방세 중 특정 재원 목적을 위해 부과되는 목적세 세목 묶음입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.local-taxes"
      ],
      "children": [
        "local.regional-resource-facility",
        "local.local-education"
      ],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.local-taxes",
      "title": "지방세",
      "type": "category",
      "description": "지방자치단체가 과세권을 가지는 지방세기본법 제8조상 세목 전체입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "category.local-ordinary-taxes",
        "category.local-purpose-taxes"
      ],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "complete-manifest"
      ]
    },
    {
      "id": "category.national-taxes",
      "title": "국세",
      "type": "category",
      "description": "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목 전체입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
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
        "tax.special-rural-development"
      ],
      "related": [],
      "terms": [
        "term.national-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "complete-manifest"
      ]
    },
    {
      "id": "category.policy-supports",
      "title": "정책지원금·세제지원 계좌",
      "type": "category",
      "description": "국세청 현금성 지원금, 정부24 복지급여, 금융위원회·금융공공기관의 자산형성·서민금융·주거금융·채무조정 지원을 학습용으로 묶은 항목입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "kr-tax-system"
      ],
      "children": [
        "support.earned-income-tax-credit",
        "support.child-tax-credit",
        "support.basic-livelihood-benefit",
        "support.youth-future-savings",
        "support.youth-leap-account",
        "support.isa",
        "support.illegal-private-finance-prevention-loan",
        "support.hessal-loan-youth",
        "support.hessal-119",
        "support.didimdol-loan",
        "support.youth-special-rent-guarantee",
        "support.long-term-delinquent-debt-adjustment"
      ],
      "related": [],
      "terms": [
        "term.total-income",
        "term.gross-pay",
        "term.property-requirement",
        "term.eligibility-threshold",
        "term.median-income",
        "term.policy-finance",
        "term.policy-loan",
        "term.debt-adjustment"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.eitc.intro",
        "source.nts.ctc.intro",
        "source.govkr.basic-livelihood-benefit",
        "source.fsc.youth-future-savings",
        "source.kinfa.youth-leap",
        "source.kinfa.illegal-private-finance-prevention-loan",
        "source.kinfa.hessal-loan-youth",
        "source.kinfa.hessal-119",
        "source.hf.didimdol-loan",
        "source.hf.special-rent-guarantee",
        "source.ccrs.long-term-delinquent-debt-adjustment",
        "source.fsc.isa.policy"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.tax-credits",
      "title": "세액공제",
      "type": "category",
      "description": "산출세액에서 직접 차감하는 공제 항목 묶음입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.deductions-and-reliefs"
      ],
      "children": [
        "credit.earned-income",
        "credit.child",
        "credit.pension-account",
        "credit.special-tax",
        "credit.monthly-rent",
        "credit.foreign-tax-paid",
        "credit.research-and-development",
        "credit.integrated-employment"
      ],
      "related": [
        "tax.income"
      ],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.year-end-settlement.special-credit",
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "category.tax-reductions",
      "title": "세액감면",
      "type": "category",
      "description": "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 감면 항목 묶음입니다.",
      "folder": "20_Deductions/TaxReductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.deductions-and-reliefs"
      ],
      "children": [
        "reduction.sme-employment-income",
        "reduction.startup-sme",
        "reduction.sme-special",
        "reduction.good-landlord"
      ],
      "related": [],
      "terms": [
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": []
    },
    {
      "id": "concept.capital-gains.calculation-flow",
      "title": "양도소득세 계산 흐름",
      "type": "concept",
      "description": "양도가액, 취득가액, 필요경비, 장기보유특별공제, 기본공제 등을 거쳐 양도소득 과세표준과 산출세액을 파악하는 계산 구조입니다.",
      "folder": "10_Taxes/National/CapitalGains",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.income.capital-gains"
      ],
      "children": [],
      "related": [
        "filing.capital-gains-return"
      ],
      "terms": [
        "term.capital-gain",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.capital-gains.overview",
        "source.nts.capital-gains.basic-deduction"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "양도소득 과세표준 산식",
          "basis": "양도가액·취득가액·필요경비·공제",
          "condition": "양도소득이 발생한 경우",
          "amount_formula": "양도가액 - 취득가액 - 필요경비 - 장기보유특별공제 - 양도소득 기본공제",
          "source": "source.nts.capital-gains.overview"
        },
        {
          "label": "양도소득 기본공제",
          "basis": "자산군별 양도소득금액",
          "condition": "해당 과세기간 자산군별 적용",
          "deduction_krw": 2500000,
          "source": "source.nts.capital-gains.basic-deduction"
        }
      ]
    },
    {
      "id": "concept.capital-gains.stock-basic-deduction",
      "title": "주식 등 양도소득 기본공제",
      "type": "concept",
      "description": "주식 등 양도소득은 국내·국외주식 등 그룹별 기본공제 적용 여부를 확인해야 하며, 증권거래세와 별도로 양도차익 과세 흐름을 관리합니다.",
      "folder": "10_Taxes/National/CapitalGains",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.income.capital-gains"
      ],
      "children": [],
      "related": [
        "tax.securities-transaction",
        "filing.capital-gains-return"
      ],
      "terms": [
        "term.capital-gain"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.capital-gains.overview",
        "source.nts.capital-gains.basic-deduction"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "주식 등 양도소득 기본공제",
          "basis": "주식 등 양도소득금액",
          "condition": "해당 과세기간 주식 등 그룹",
          "deduction_krw": 2500000,
          "source": "source.nts.capital-gains.basic-deduction"
        }
      ]
    },
    {
      "id": "concept.cre-deduction-thresholds",
      "title": "종합부동산세 공제금액",
      "type": "concept",
      "description": "종합부동산세는 주택, 종합합산토지, 별도합산토지 등 과세대상별 공제금액을 먼저 차감한 뒤 과세표준을 계산합니다.",
      "folder": "10_Taxes/National/RealEstate",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.comprehensive-real-estate"
      ],
      "children": [],
      "related": [
        "local.property"
      ],
      "terms": [
        "term.publicly-notified-price",
        "term.tax-base",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.comprehensive-real-estate.overview"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "주택 공제금액",
          "basis": "공시가격 합계액",
          "condition": "주택",
          "deduction_krw": 900000000,
          "note": "1세대 1주택자는 12억원",
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "1세대 1주택자 주택 공제금액",
          "basis": "공시가격 합계액",
          "condition": "1세대 1주택자",
          "deduction_krw": 1200000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "종합합산토지 공제금액",
          "basis": "공시가격 합계액",
          "condition": "종합합산토지",
          "deduction_krw": 500000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "별도합산토지 공제금액",
          "basis": "공시가격 합계액",
          "condition": "별도합산토지",
          "deduction_krw": 8000000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        }
      ]
    },
    {
      "id": "concept.cre-tax-base-date",
      "title": "종합부동산세 과세기준일",
      "type": "concept",
      "description": "종합부동산세는 매년 6월 1일 현재 보유한 주택과 토지를 기준으로 재산세 과세자료와 연결해 과세대상을 판단합니다.",
      "folder": "10_Taxes/National/RealEstate",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.comprehensive-real-estate"
      ],
      "children": [],
      "related": [
        "local.property"
      ],
      "terms": [
        "term.publicly-notified-price"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.comprehensive-real-estate.overview"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "과세기준일",
          "basis": "보유일 기준",
          "condition": "매년 6월 1일 현재 보유",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.comprehensive-real-estate.overview"
        }
      ]
    },
    {
      "id": "concept.general-vat-taxpayer",
      "title": "일반과세자 기준",
      "type": "concept",
      "description": "부가가치세에서 일반 세율과 매입세액 공제 구조를 적용받는 과세사업자 유형입니다. 사업자등록과 부가가치세 신고 시 간이과세자 기준과 함께 확인합니다.",
      "folder": "40_Terms/Concepts",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.value-added"
      ],
      "children": [],
      "related": [
        "concept.simple-vat-taxpayer",
        "filing.business-registration",
        "filing.vat-return"
      ],
      "terms": [
        "term.general-vat-taxpayer",
        "term.tax-rate",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty",
        "source.nts.business-registration.application"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "일반과세자 매출 기준",
          "basis": "1년 매출액",
          "condition": "1억400만원 이상",
          "threshold_krw_min": 104000000,
          "benefit": "일반과세자",
          "source": "source.nts.vat.overview"
        },
        {
          "label": "일반과세자 세율",
          "basis": "매출세액",
          "condition": "매출액에 기본세율 적용",
          "rate_percent": 10,
          "note": "영세율 적용 대상은 0%",
          "source": "source.nts.vat.filing-duty",
          "amount_formula": "매출세액 × 적용비율 10%"
        }
      ]
    },
    {
      "id": "concept.simple-vat-taxpayer",
      "title": "간이과세자 기준",
      "type": "concept",
      "description": "부가가치세에서 1년 매출액 10,400만원 미만 개인사업자에게 적용되는 납세 유형 기준입니다. 사업자등록 단계에서 간이과세 배제 업종과 일반과세자 전환 가능성을 함께 확인합니다.",
      "folder": "40_Terms/Concepts",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.value-added"
      ],
      "children": [],
      "related": [
        "concept.general-vat-taxpayer",
        "concept.vat-payment-exemption",
        "filing.business-registration",
        "filing.vat-return"
      ],
      "terms": [
        "term.simple-vat-taxpayer",
        "term.tax-rate",
        "term.eligibility-threshold"
      ],
      "deadlines": [
        "deadline.vat.simplified.annual",
        "deadline.vat.simplified.preliminary"
      ],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty",
        "source.nts.business-registration.application"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "간이과세자 매출 기준",
          "basis": "1년 매출액",
          "condition": "1억400만원 미만",
          "threshold_krw_max": 104000000,
          "benefit": "간이과세자",
          "source": "source.nts.vat.overview"
        },
        {
          "label": "간이과세자 업종별 부가가치율",
          "basis": "업종별 부가가치율",
          "condition": "2021.7.1. 이후 업종별 15%~40%",
          "rate_percent_min": 15,
          "rate_percent_max": 40,
          "note": "납부세액은 매출액 × 업종별 부가가치율 × 10% - 공제세액",
          "source": "source.nts.vat.overview",
          "amount_formula": "업종별 부가가치율 × 적용비율 15%~40%"
        },
        {
          "label": "간이과세자 예정신고 대상",
          "basis": "직전연도 공급대가",
          "condition": "4,800만원 이상 1억400만원 미만이고 예정부과기간에 세금계산서 발급",
          "threshold_krw_min": 48000000,
          "threshold_krw_max": 104000000,
          "source": "source.nts.vat.filing-duty"
        },
        {
          "label": "간이과세자 납부의무 면제",
          "basis": "직전연도 공급대가",
          "condition": "4,800만원 미만",
          "threshold_krw_max": 48000000,
          "benefit": "납부세액 납부의무 면제 가능",
          "source": "source.nts.vat.filing-duty"
        }
      ]
    },
    {
      "id": "concept.vat-payment-exemption",
      "title": "간이과세자 납부의무 면제",
      "type": "concept",
      "description": "직전연도 공급대가가 일정 금액 미만인 간이과세자는 부가가치세 납부세액의 납부의무가 면제될 수 있어 신고와 납부 판단을 분리해 확인해야 합니다.",
      "folder": "40_Terms/Concepts",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.value-added"
      ],
      "children": [],
      "related": [
        "concept.simple-vat-taxpayer",
        "filing.vat-return"
      ],
      "terms": [
        "term.simple-vat-taxpayer",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "간이과세자 납부의무 면제",
          "basis": "직전연도 공급대가",
          "condition": "4,800만원 미만",
          "threshold_krw_max": 48000000,
          "benefit": "납부세액 납부의무 면제 가능",
          "source": "source.nts.vat.filing-duty"
        }
      ]
    },
    {
      "id": "corporate.support.agricultural-corporation-reduction",
      "title": "영농조합법인 등에 대한 감면",
      "type": "corporate-tax-support",
      "description": "영농조합법인, 영어조합법인, 농업회사법인 등의 농어업소득 등에 대한 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "농업소득",
          "basis": "영농조합법인 등 농업소득",
          "condition": "농업법인 요건 충족",
          "rate_percent": 100,
          "rate_label": "면제율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "영농조합법인 등 농업소득 × 면제율 100%"
        },
        {
          "label": "농업 외 소득",
          "basis": "농업 외 소득",
          "condition": "한도 내 감면",
          "rate_percent": 50,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "농업 외 소득 × 감면율 50%"
        }
      ]
    },
    {
      "id": "corporate.support.cooperation-credit",
      "title": "상생협력에 대한 조세지원",
      "type": "corporate-tax-support",
      "description": "협력중소기업 지원 목적 출연금과 유형고정자산 무상임대 등에 대한 조세지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "상생협력 출연금",
          "basis": "협력중소기업 지원 목적 출연금 등",
          "condition": "상생협력 지원 요건 충족",
          "rate_percent": 10,
          "rate_label": "세액공제율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "협력중소기업 지원 목적 출연금 등 × 세액공제율 10%"
        }
      ]
    },
    {
      "id": "corporate.support.crisis-area-startup-reduction",
      "title": "위기지역 창업기업 감면",
      "type": "corporate-tax-support",
      "description": "위기지역 지정 또는 선포 기간에 창업하거나 사업장을 신설한 기업에 대한 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "위기지역 창업기업",
          "basis": "법인세",
          "condition": "위기지역 지정 또는 선포 기간 창업·사업장 신설",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "note": "감면기간 및 지역별 요건 별도 확인",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.disaster-loss-credit",
      "title": "재해손실세액공제",
      "type": "corporate-tax-support",
      "description": "천재지변 등 재해로 사업용 총자산가액의 20% 이상을 상실한 경우 적용되는 법인세법상 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "재해손실세액공제",
          "basis": "재해상실자산가액 / 상실 전 자산총액",
          "condition": "사업용 총자산가액의 20% 이상 상실",
          "rate_percent": 20,
          "rate_label": "상실비율 문턱",
          "benefit": "산출세액에 재해상실비율을 곱해 공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "재해상실자산가액 / 상실 전 자산총액 × 상실비율 문턱 20%"
        }
      ]
    },
    {
      "id": "corporate.support.e-filing-credit",
      "title": "전자신고 세액공제",
      "type": "corporate-tax-support",
      "description": "법인이 직접 법인세를 전자신고할 때 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "전자신고 세액공제",
          "basis": "법인세 전자신고",
          "condition": "법인이 직접 전자신고",
          "deduction_krw": 10000,
          "source": "source.nts.corporate-tax.reliefs"
        }
      ]
    },
    {
      "id": "corporate.support.employment-maintenance-credit",
      "title": "고용유지 중소기업 등에 대한 과세특례",
      "type": "corporate-tax-support",
      "description": "임금 감소와 시간당 임금 보전액 등을 기준으로 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "고용유지 임금감소분",
          "basis": "임금감소액 또는 보전액",
          "condition": "고용유지 요건 충족",
          "rate_percent": 50,
          "rate_label": "공제율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "임금감소액 또는 보전액 × 공제율 50%"
        }
      ]
    },
    {
      "id": "corporate.support.enterprise-city-reduction",
      "title": "기업도시개발구역 창업기업 등 감면",
      "type": "corporate-tax-support",
      "description": "기업도시개발구역 창업 또는 사업장 신설 기업에 적용되는 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "기업도시개발구역 창업·신설",
          "basis": "법인세",
          "condition": "기업도시개발구역 창업 또는 사업장 신설",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.facility-investment-credit",
      "title": "시설투자 등에 대한 세액공제",
      "type": "corporate-tax-support",
      "description": "각종 시설투자 금액과 투자 증가분에 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "통합투자 기본공제",
          "basis": "사업용 유형자산 등 투자금액",
          "condition": "통합투자세액공제 대상 투자",
          "rate_percent_min": 1,
          "rate_percent_max": 10,
          "rate_label": "기본공제율",
          "note": "기업규모·투자자산 유형별 차등",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "사업용 유형자산 등 투자금액 × 기본공제율 1%~10%"
        },
        {
          "label": "투자증가분 추가공제",
          "basis": "직전 3년 평균 투자액 초과분",
          "condition": "투자 증가",
          "rate_percent": 10,
          "rate_label": "추가공제율",
          "note": "추가공제 한도는 기본공제 금액의 2배",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "직전 3년 평균 투자액 초과분 × 추가공제율 10%"
        }
      ]
    },
    {
      "id": "corporate.support.foreign-tax-paid-credit",
      "title": "외국납부세액공제",
      "type": "corporate-tax-support",
      "description": "국외원천소득에 대한 이중과세 조정을 위한 법인세법상 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [
        "credit.foreign-tax-paid"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "외국납부세액공제 한도",
          "basis": "국외원천소득 관련 외국납부세액",
          "condition": "국내 산출세액 중 국외원천소득 비율 상당액 한도",
          "benefit": "외국납부세액과 한도액 중 작은 금액 공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "corporate.support.good-landlord-credit",
      "title": "상가임대료 인하 임대사업자 세액공제",
      "type": "corporate-tax-support",
      "description": "상가건물 임대료 인하액에 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [
        "reduction.good-landlord"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "임대료 인하액",
          "basis": "상가건물 임대료 인하액",
          "condition": "소상공인 임차인 임대료 인하 등 요건 충족",
          "rate_percent": 70,
          "rate_label": "세액공제율",
          "note": "요건과 과세연도별 적용기한 확인 필요",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "상가건물 임대료 인하액 × 세액공제율 70%"
        }
      ]
    },
    {
      "id": "corporate.support.industrial-complex-reduction",
      "title": "농공단지 등 입주 기업 감면",
      "type": "corporate-tax-support",
      "description": "농공단지 등 입주 후 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "농공단지 등 입주기업",
          "basis": "법인세",
          "condition": "농공단지 등 입주 후 최초 소득발생",
          "rate_percent": 50,
          "rate_label": "감면율",
          "note": "감면기간 요건 별도 확인",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%"
        }
      ]
    },
    {
      "id": "corporate.support.jeju-zone-reduction",
      "title": "제주첨단과학기술단지 등 입주 감면",
      "type": "corporate-tax-support",
      "description": "제주첨단과학기술단지 또는 제주투자진흥지구 입주기업 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "제주첨단과학기술단지 등",
          "basis": "법인세",
          "condition": "제주첨단과학기술단지 또는 제주투자진흥지구 입주",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.local-relocation-deferral",
      "title": "지방이전 촉진 과세이연",
      "type": "corporate-tax-support",
      "description": "지방이전 등을 촉진하기 위한 양도차익 등의 손금산입 또는 익금불산입 지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "지방이전 과세이연",
          "basis": "지방이전 관련 양도차익 등",
          "condition": "지방이전 촉진 요건 충족",
          "benefit": "손금산입 또는 익금불산입으로 과세이연",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "corporate.support.local-relocation-reduction",
      "title": "공장·본사 등 지방이전 세액감면",
      "type": "corporate-tax-support",
      "description": "수도권과밀억제권역 본사·공장 지방 이전 등에 적용되는 세액감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "수도권 밖 이전 감면",
          "basis": "법인세",
          "condition": "공장·본사 등 지방 이전 요건 충족",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "note": "지역과 기간별 차등",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.ma-credit",
      "title": "M&A 활성화 지원",
      "type": "corporate-tax-support",
      "description": "기술혁신형 합병·주식취득 인수가액 중 기술가치 금액에 대한 법인세 공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "기술혁신형 M&A",
          "basis": "인수가액 중 기술가치 금액",
          "condition": "기술혁신형 합병·주식취득",
          "rate_percent": 10,
          "rate_label": "세액공제율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "인수가액 중 기술가치 금액 × 세액공제율 10%"
        }
      ]
    },
    {
      "id": "corporate.support.minimum-tax-preference",
      "title": "최저한세 적용한도 우대",
      "type": "corporate-tax-support",
      "description": "중소기업 등에게 일반법인보다 우대되는 최저한세율을 적용하는 지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "중소기업 최저한세",
          "basis": "각종 감면 전 과세표준",
          "condition": "중소기업",
          "rate_percent": 7,
          "rate_label": "최저한세율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "각종 감면 전 과세표준 × 최저한세율 7%"
        }
      ]
    },
    {
      "id": "corporate.support.performance-sharing-credit",
      "title": "성과공유 중소기업의 경영성과급 세액공제",
      "type": "corporate-tax-support",
      "description": "중소기업이 요건을 충족한 경영성과급을 지급하는 경우 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "경영성과급",
          "basis": "성과공유 중소기업 경영성과급 지급액",
          "condition": "성과공유기업 요건 충족",
          "rate_percent": 15,
          "rate_label": "세액공제율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "성과공유 중소기업 경영성과급 지급액 × 세액공제율 15%"
        }
      ]
    },
    {
      "id": "corporate.support.restructuring-deferral",
      "title": "구조조정 및 재무구조개선 과세이연",
      "type": "corporate-tax-support",
      "description": "양도차익 등에 대한 손금산입 또는 익금불산입 등 구조조정 지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "구조조정 과세이연",
          "basis": "양도차익 등",
          "condition": "구조조정 및 재무구조개선 요건 충족",
          "benefit": "손금산입 또는 익금불산입으로 과세이연",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "corporate.support.rnd-credit",
      "title": "연구·인력개발비 세액공제",
      "type": "corporate-tax-support",
      "description": "일반, 신성장·원천기술, 국가전략기술 연구개발비에 대한 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [
        "credit.research-and-development"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "일반 연구·인력개발비",
          "basis": "연구·인력개발비",
          "condition": "기업규모·증가분 방식별 공제율 적용",
          "benefit": "일반 R&D 세액공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "신성장·원천기술",
          "basis": "신성장·원천기술 연구개발비",
          "condition": "해당 기술 연구개발비",
          "benefit": "우대 공제율 적용",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "국가전략기술",
          "basis": "국가전략기술 연구개발비",
          "condition": "반도체 등 국가전략기술 연구개발비",
          "benefit": "최고 우대 공제율 적용",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "corporate.support.rnd-grant-deferral",
      "title": "연구개발 관련 출연금등의 과세이연",
      "type": "corporate-tax-support",
      "description": "연구개발출연금 등에 대한 익금불산입 지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "연구개발출연금 과세이연",
          "basis": "연구개발출연금 등",
          "condition": "연구개발 자산 취득 또는 비용 지출",
          "benefit": "익금불산입 후 사용 시점에 익금산입",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "corporate.support.rnd-zone-reduction",
      "title": "연구개발특구 입주 기업 감면",
      "type": "corporate-tax-support",
      "description": "첨단기술 및 연구소기업 등에 적용되는 법인세 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "연구개발특구 감면",
          "basis": "법인세",
          "condition": "연구개발특구 입주 첨단기술기업 등",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "note": "일반적으로 3년 100%, 이후 2년 50% 구조",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.sme-special-reduction",
      "title": "중소기업특별세액감면",
      "type": "corporate-tax-support",
      "description": "제조업 등 일정 업종 중소기업 소득에 대한 법인세 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [
        "reduction.sme-special"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "소기업 수도권 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "소기업, 수도권 내 제조업·출판업 등",
          "rate_percent": 20,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 20%"
        },
        {
          "label": "소기업 수도권 외 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "소기업, 수도권 외 제조업·출판업 등",
          "rate_percent": 30,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 30%"
        },
        {
          "label": "중기업 수도권 외 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "중기업, 수도권 외 제조업 등",
          "rate_percent": 15,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 15%"
        },
        {
          "label": "도소매·의료업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "업종·지역별 차등",
          "rate_percent_min": 5,
          "rate_percent_max": 10,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 5%~10%"
        }
      ]
    },
    {
      "id": "corporate.support.social-enterprise-reduction",
      "title": "사회적기업 등에 대한 감면",
      "type": "corporate-tax-support",
      "description": "사회적기업 인증 법인과 장애인 표준사업장 등에 적용되는 감면입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "사회적기업·장애인 표준사업장",
          "basis": "법인세",
          "condition": "인증 사회적기업 등",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "감면율",
          "note": "일반적으로 3년 100%, 이후 2년 50% 구조",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "법인세 × 감면율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.social-insurance-credit",
      "title": "사회보험료 세액공제",
      "type": "corporate-tax-support",
      "description": "고용증가인원의 사회보험료 상당액에 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "고용증가 사회보험료",
          "basis": "고용증가인원의 사용자 부담 사회보험료",
          "condition": "상시근로자 증가",
          "rate_percent_min": 50,
          "rate_percent_max": 100,
          "rate_label": "세액공제율",
          "note": "청년·경력단절자 등 우대 대상과 기업규모별 차등",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "고용증가인원의 사용자 부담 사회보험료 × 세액공제율 50%~100%"
        }
      ]
    },
    {
      "id": "corporate.support.startup-sme-reduction",
      "title": "창업중소기업 등에 대한 세액감면",
      "type": "corporate-tax-support",
      "description": "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 법인세 조세지원입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [
        "reduction.startup-sme"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "2026년 이후 일반 창업중소기업",
          "basis": "법인세 또는 소득세",
          "condition": "수도권 외 지역 또는 수도권 인구감소지역",
          "rate_percent": 50,
          "rate_label": "감면율",
          "note": "최초 소득발생 과세연도와 이후 4년",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "법인세 또는 소득세 × 감면율 50%"
        },
        {
          "label": "2026년 이후 청년·생계형 창업",
          "basis": "법인세 또는 소득세",
          "condition": "수도권 외 지역 또는 수도권과밀억제권역 외",
          "rate_percent": 100,
          "rate_label": "감면율",
          "note": "수도권 과밀억제권역 50%, 수도권 75% 등 지역별 차등",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "법인세 또는 소득세 × 감면율 100%"
        },
        {
          "label": "상시근로자 증가 추가감면",
          "basis": "상시근로자 증가율",
          "condition": "고용 증가 요건 충족",
          "rate_percent": 100,
          "rate_label": "추가감면 산식",
          "note": "상시근로자 증가율 × 100%",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "상시근로자 증가율 × 추가감면 산식 100%"
        }
      ]
    },
    {
      "id": "corporate.support.tech-transfer-reduction",
      "title": "기술이전·대여 세액감면",
      "type": "corporate-tax-support",
      "description": "기술이전 및 기술취득 등에 대한 과세특례입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "기술이전 소득",
          "basis": "기술이전 소득",
          "condition": "중소기업 기술이전",
          "rate_percent": 50,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "기술이전 소득 × 감면율 50%"
        },
        {
          "label": "기술대여 소득",
          "basis": "기술대여 소득",
          "condition": "중소기업 기술대여",
          "rate_percent": 25,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "기술대여 소득 × 감면율 25%"
        }
      ]
    },
    {
      "id": "corporate.support.wage-increase-credit",
      "title": "근로소득을 증대시킨 기업에 대한 세액공제",
      "type": "corporate-tax-support",
      "description": "임금 증가와 정규직 전환 근로자 임금 증가 등에 대한 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "근로소득 증대",
          "basis": "직전 3년 평균 초과 임금증가분",
          "condition": "임금증가 요건 충족",
          "rate_percent_min": 5,
          "rate_percent_max": 20,
          "rate_label": "세액공제율",
          "note": "기업규모와 정규직 전환 여부별 차등",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "직전 3년 평균 초과 임금증가분 × 세액공제율 5%~20%"
        }
      ]
    },
    {
      "id": "corporate.support.winwin-payment-credit",
      "title": "상생결제 지급금액 세액공제",
      "type": "corporate-tax-support",
      "description": "상생결제제도를 통해 구매대금을 지급한 경우 적용되는 세액공제입니다.",
      "folder": "20_Deductions/CorporateTaxSupports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.corporate-tax-supports"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "corporate-tax-support"
      ],
      "criteria": [
        {
          "label": "상생결제 지급금액",
          "basis": "상생결제 지급금액",
          "condition": "상생결제제도 이용 구매대금 지급",
          "rate_percent_min": 0.1,
          "rate_percent_max": 0.3,
          "rate_label": "세액공제율",
          "note": "결제기한 구간별 차등",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "상생결제 지급금액 × 세액공제율 0.1%~0.3%"
        }
      ]
    },
    {
      "id": "credit.child",
      "title": "자녀 세액공제",
      "type": "tax-credit",
      "description": "자녀 수 등 요건에 따라 산출세액에서 차감되는 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [
        "support.child-tax-credit"
      ],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "자녀 1명",
          "basis": "8세 이상 기본공제대상 자녀·손자녀",
          "condition": "1명",
          "deduction_krw": 250000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "자녀 2명",
          "basis": "8세 이상 기본공제대상 자녀·손자녀",
          "condition": "2명",
          "deduction_krw": 550000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "자녀 3명 이상",
          "basis": "8세 이상 기본공제대상 자녀·손자녀",
          "condition": "3명 이상",
          "deduction_krw": 550000,
          "note": "2명을 초과하는 1명당 40만원 추가",
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "출산·입양 첫째",
          "basis": "출산·입양 신고 자녀",
          "condition": "첫째",
          "deduction_krw": 300000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "출산·입양 둘째",
          "basis": "출산·입양 신고 자녀",
          "condition": "둘째",
          "deduction_krw": 500000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "출산·입양 셋째 이상",
          "basis": "출산·입양 신고 자녀",
          "condition": "셋째 이상",
          "deduction_krw": 700000,
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "credit.donation",
      "title": "기부금 세액공제",
      "type": "tax-credit",
      "description": "정치자금, 고향사랑, 특례, 우리사주조합, 일반기부금 등 공제한도 내 기부금에 대한 특별세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "credit.special-tax"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.special-credit"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "정치자금 10만원 이하",
          "basis": "정치자금기부금",
          "condition": "10만원 이하",
          "threshold_krw_max": 100000,
          "rate_percent": 90.91,
          "rate_label": "세액공제율",
          "note": "100/110 세액공제",
          "source": "source.nts.donation-credit"
        },
        {
          "label": "정치자금 10만원 초과",
          "basis": "정치자금기부금",
          "condition": "10만원 초과",
          "threshold_krw_min": 100000,
          "rate_percent": 15,
          "source": "source.nts.donation-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "정치자금 3천만원 초과",
          "basis": "정치자금기부금",
          "condition": "3천만원 초과분",
          "threshold_krw_min": 30000000,
          "rate_percent": 25,
          "source": "source.nts.donation-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "고향사랑 10만원 이하",
          "basis": "고향사랑기부금",
          "condition": "10만원 이하",
          "threshold_krw_max": 100000,
          "rate_percent": 90.91,
          "rate_label": "세액공제율",
          "note": "100/110 세액공제",
          "source": "source.nts.donation-credit"
        },
        {
          "label": "특례·우리사주·일반 1천만원 이하",
          "basis": "공제한도 내 기부금",
          "condition": "1천만원 이하",
          "threshold_krw_max": 10000000,
          "rate_percent": 15,
          "source": "source.nts.donation-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "특례·우리사주·일반 1천만원 초과",
          "basis": "공제한도 내 기부금",
          "condition": "1천만원 초과",
          "threshold_krw_min": 10000000,
          "rate_percent": 30,
          "source": "source.nts.donation-credit",
          "rate_label": "세액공제율"
        }
      ]
    },
    {
      "id": "credit.earned-income",
      "title": "근로소득 세액공제",
      "type": "tax-credit",
      "description": "근로소득자의 산출세액에서 차감되는 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "산출세액 130만원 이하",
          "basis": "근로소득 산출세액",
          "condition": "130만원 이하",
          "threshold_krw_max": 1300000,
          "rate_percent": 55,
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "세액공제율"
        },
        {
          "label": "산출세액 130만원 초과",
          "basis": "근로소득 산출세액",
          "condition": "130만원 초과",
          "threshold_krw_min": 1300000,
          "deduction_krw": 715000,
          "rate_percent": 30,
          "note": "715,000원 + 130만원 초과금액의 30%",
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "세액공제율"
        },
        {
          "label": "총급여 3,300만원 이하 한도",
          "basis": "총급여",
          "condition": "3,300만원 이하",
          "threshold_krw_max": 33000000,
          "limit_krw": 740000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "총급여 3,300만원 초과 7,000만원 이하 한도",
          "basis": "총급여",
          "condition": "3,300만원 초과 7,000만원 이하",
          "threshold_krw_min": 33000000,
          "threshold_krw_max": 70000000,
          "limit_krw": 660000,
          "note": "74만원-[(총급여액-3,300만원)×0.8%], 최소 66만원",
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "총급여 7,000만원 초과 1.2억원 이하 한도",
          "basis": "총급여",
          "condition": "7,000만원 초과 1.2억원 이하",
          "threshold_krw_min": 70000000,
          "threshold_krw_max": 120000000,
          "limit_krw": 500000,
          "note": "66만원-[(총급여액-7,000만원)×1/2], 최소 50만원",
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "총급여 1.2억원 초과 한도",
          "basis": "총급여",
          "condition": "1.2억원 초과",
          "threshold_krw_min": 120000000,
          "limit_krw": 200000,
          "note": "50만원-[(총급여액-1.2억원)×1/2], 최소 20만원",
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "credit.education-expense",
      "title": "교육비 세액공제",
      "type": "tax-credit",
      "description": "본인과 기본공제대상자 교육비 등에 대한 특별세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "credit.special-tax"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.special-credit"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "본인 교육비",
          "basis": "근로자 본인 교육비",
          "condition": "한도 없음",
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율",
          "amount_formula": "근로자 본인 교육비 × 세액공제율 15%"
        },
        {
          "label": "취학전·초중고 교육비",
          "basis": "부양가족 1명당 교육비",
          "condition": "취학전 아동, 초·중·고등학생",
          "limit_krw": 3000000,
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "대학생 교육비",
          "basis": "부양가족 1명당 교육비",
          "condition": "대학생",
          "limit_krw": 9000000,
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "장애인 특수교육비",
          "basis": "장애인 특수교육비",
          "condition": "직계존속 포함, 소득제한 없음",
          "rate_percent": 15,
          "note": "한도 없음",
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율",
          "amount_formula": "장애인 특수교육비 × 세액공제율 15%"
        }
      ]
    },
    {
      "id": "credit.foreign-tax-paid",
      "title": "외국납부세액공제",
      "type": "tax-credit",
      "description": "국외원천소득에 대한 이중과세 조정을 위한 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [
        "corporate.support.foreign-tax-paid-credit"
      ],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "외국납부세액공제 한도",
          "basis": "국외원천소득 관련 외국납부세액",
          "condition": "국내 산출세액 중 국외원천소득 비율 상당액 한도",
          "benefit": "외국납부세액과 한도액 중 작은 금액 공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "credit.insurance-premium",
      "title": "보험료 세액공제",
      "type": "tax-credit",
      "description": "보장성보험료, 장애인전용 보장성보험료 등에 대한 특별세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "credit.special-tax"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.special-credit"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "보장성보험료",
          "basis": "생명보험·상해보험 등 보장성보험료",
          "condition": "기본공제대상자를 위해 지급",
          "limit_krw": 1000000,
          "rate_percent": 12,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "장애인전용 보장성보험료",
          "basis": "장애인을 피보험자 또는 수익자로 하는 장애인전용 보장성보험료",
          "condition": "장애인전용 보장성보험",
          "limit_krw": 1000000,
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        }
      ]
    },
    {
      "id": "credit.integrated-employment",
      "title": "통합고용세액공제",
      "type": "tax-credit",
      "description": "고용 증가, 청년·장애인·경력단절자 등 정책 대상 고용에 대한 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "고용 증가 인원",
          "basis": "상시근로자 증가 인원",
          "condition": "전년 대비 고용 증가",
          "benefit": "1인당 정액 세액공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "우대 대상 고용",
          "basis": "청년·장애인·경력단절자 등",
          "condition": "정책대상 근로자 고용 증가",
          "benefit": "일반 상시근로자보다 우대 공제액 적용",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "credit.medical-expense",
      "title": "의료비 세액공제",
      "type": "tax-credit",
      "description": "총급여액의 일정 비율 초과 의료비 등에 대한 특별세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "credit.special-tax"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.special-credit"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "의료비 공제 문턱",
          "basis": "의료비 지출액",
          "condition": "총급여액의 3% 초과분",
          "rate_percent": 3,
          "note": "초과분이 공제대상 의료비",
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "의료비 지출액 × 세액공제율 3%"
        },
        {
          "label": "일반 의료비",
          "basis": "일반 기본공제대상자 의료비",
          "condition": "연 700만원 한도",
          "limit_krw": 7000000,
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "본인·6세 이하·65세 이상·장애인 의료비",
          "basis": "해당 의료비",
          "condition": "한도 없음",
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "해당 의료비 × 세액공제율 15%"
        },
        {
          "label": "난임시술비",
          "basis": "난임시술비",
          "condition": "한도 없음",
          "rate_percent": 30,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "난임시술비 × 세액공제율 30%"
        }
      ]
    },
    {
      "id": "credit.monthly-rent",
      "title": "월세액 세액공제",
      "type": "tax-credit",
      "description": "무주택, 총급여·종합소득금액, 주택 요건 등을 충족한 월세액에 대한 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [
        "support.didimdol-loan",
        "support.youth-special-rent-guarantee"
      ],
      "terms": [
        "term.tax-credit",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.monthly-rent-credit"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "공제대상자 소득",
          "basis": "총급여",
          "condition": "8,000만원 이하",
          "threshold_krw_max": 80000000,
          "source": "source.nts.monthly-rent-credit"
        },
        {
          "label": "공제대상자 종합소득",
          "basis": "종합소득금액",
          "condition": "7,000만원 이하",
          "threshold_krw_max": 70000000,
          "source": "source.nts.monthly-rent-credit"
        },
        {
          "label": "17% 공제율",
          "basis": "총급여",
          "condition": "5,500만원 이하",
          "threshold_krw_max": 55000000,
          "rate_percent": 17,
          "limit_krw": 10000000,
          "source": "source.nts.monthly-rent-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "15% 공제율",
          "basis": "총급여",
          "condition": "5,500만원 초과 8,000만원 이하",
          "threshold_krw_min": 55000000,
          "threshold_krw_max": 80000000,
          "rate_percent": 15,
          "limit_krw": 10000000,
          "source": "source.nts.monthly-rent-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "공제대상 주택",
          "basis": "주택 규모·기준시가",
          "condition": "국민주택규모 또는 기준시가 4억원 이하",
          "threshold_krw_max": 400000000,
          "source": "source.nts.monthly-rent-credit"
        }
      ]
    },
    {
      "id": "credit.pension-account",
      "title": "연금계좌 세액공제",
      "type": "tax-credit",
      "description": "연금저축, 퇴직연금계좌 납입액 등에 대한 세액공제입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-credit",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "총급여 5,500만원 이하",
          "basis": "총급여 또는 종합소득금액",
          "condition": "총급여 5,500만원 이하 또는 종합소득금액 4,500만원 이하",
          "threshold_krw_max": 55000000,
          "limit_krw": 9000000,
          "rate_percent": 15,
          "note": "연금저축 600만원, 퇴직연금 포함 900만원 한도",
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "세액공제율"
        },
        {
          "label": "총급여 5,500만원 초과",
          "basis": "총급여 또는 종합소득금액",
          "condition": "총급여 5,500만원 초과",
          "threshold_krw_min": 55000000,
          "limit_krw": 9000000,
          "rate_percent": 12,
          "note": "연금저축 600만원, 퇴직연금 포함 900만원 한도",
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "세액공제율"
        }
      ]
    },
    {
      "id": "credit.research-and-development",
      "title": "연구·인력개발비 세액공제",
      "type": "tax-credit",
      "description": "일반, 신성장·원천기술, 국가전략기술 연구개발비 등에 대한 조세지원입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [],
      "related": [
        "corporate.support.rnd-credit"
      ],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "tax-credit"
      ],
      "criteria": [
        {
          "label": "일반 연구·인력개발비",
          "basis": "연구·인력개발비",
          "condition": "기업규모·증가분 방식별 공제율 적용",
          "benefit": "일반 R&D 세액공제",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "신성장·원천기술",
          "basis": "신성장·원천기술 연구개발비",
          "condition": "해당 기술 연구개발비",
          "benefit": "우대 공제율 적용",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "국가전략기술",
          "basis": "국가전략기술 연구개발비",
          "condition": "반도체 등 국가전략기술 연구개발비",
          "benefit": "최고 우대 공제율 적용",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "credit.special-tax",
      "title": "특별세액공제",
      "type": "tax-credit",
      "description": "근로소득자가 해당 과세기간에 지출한 일정 비용을 산출세액에서 공제하는 항목 묶음입니다.",
      "folder": "20_Deductions/TaxCredits",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-credits"
      ],
      "children": [
        "credit.insurance-premium",
        "credit.medical-expense",
        "credit.education-expense",
        "credit.donation"
      ],
      "related": [],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.special-credit",
        "source.nts.education-expense-credit",
        "source.nts.donation-credit"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "보장성보험료",
          "basis": "생명보험·상해보험 등 보장성보험료",
          "condition": "기본공제대상자를 위해 지급",
          "limit_krw": 1000000,
          "rate_percent": 12,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "장애인전용 보장성보험료",
          "basis": "장애인을 피보험자 또는 수익자로 하는 장애인전용 보장성보험료",
          "condition": "장애인전용 보장성보험",
          "limit_krw": 1000000,
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "의료비 공제 문턱",
          "basis": "의료비 지출액",
          "condition": "총급여액의 3% 초과분",
          "rate_percent": 3,
          "note": "초과분이 공제대상 의료비",
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "의료비 지출액 × 세액공제율 3%"
        },
        {
          "label": "일반 의료비",
          "basis": "일반 기본공제대상자 의료비",
          "condition": "연 700만원 한도",
          "limit_krw": 7000000,
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "본인·6세 이하·65세 이상·장애인 의료비",
          "basis": "해당 의료비",
          "condition": "한도 없음",
          "rate_percent": 15,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "해당 의료비 × 세액공제율 15%"
        },
        {
          "label": "난임시술비",
          "basis": "난임시술비",
          "condition": "한도 없음",
          "rate_percent": 30,
          "source": "source.nts.year-end-settlement.special-credit",
          "rate_label": "세액공제율",
          "amount_formula": "난임시술비 × 세액공제율 30%"
        },
        {
          "label": "본인 교육비",
          "basis": "근로자 본인 교육비",
          "condition": "한도 없음",
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율",
          "amount_formula": "근로자 본인 교육비 × 세액공제율 15%"
        },
        {
          "label": "취학전·초중고 교육비",
          "basis": "부양가족 1명당 교육비",
          "condition": "취학전 아동, 초·중·고등학생",
          "limit_krw": 3000000,
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "대학생 교육비",
          "basis": "부양가족 1명당 교육비",
          "condition": "대학생",
          "limit_krw": 9000000,
          "rate_percent": 15,
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율"
        },
        {
          "label": "장애인 특수교육비",
          "basis": "장애인 특수교육비",
          "condition": "직계존속 포함, 소득제한 없음",
          "rate_percent": 15,
          "note": "한도 없음",
          "source": "source.nts.education-expense-credit",
          "rate_label": "세액공제율",
          "amount_formula": "장애인 특수교육비 × 세액공제율 15%"
        },
        {
          "label": "정치자금 10만원 이하",
          "basis": "정치자금기부금",
          "condition": "10만원 이하",
          "threshold_krw_max": 100000,
          "rate_percent": 90.91,
          "rate_label": "세액공제율",
          "note": "100/110 세액공제",
          "source": "source.nts.donation-credit"
        },
        {
          "label": "정치자금 10만원 초과",
          "basis": "정치자금기부금",
          "condition": "10만원 초과",
          "threshold_krw_min": 100000,
          "rate_percent": 15,
          "source": "source.nts.donation-credit",
          "rate_label": "세액공제율"
        }
      ]
    },
    {
      "id": "deadline.capital-gains.final",
      "title": "양도소득세 확정신고",
      "type": "deadline",
      "description": "양도소득세 확정신고는 양도한 연도의 다음연도 5월 1일부터 5월 31일까지입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.capital-gains.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2027-05-01",
      "end_date": "2027-05-31"
    },
    {
      "id": "deadline.capital-gains.preliminary",
      "title": "양도소득세 예정신고",
      "type": "deadline",
      "description": "토지·건물·부동산에 관한 권리·기타자산은 양도일이 속하는 달의 말일부터 2개월 이내, 주식·출자지분은 양도일이 속하는 반기의 말일부터 2개월 이내 예정신고합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.capital-gains.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.gift.general",
      "title": "증여세 일반 증여 신고납부",
      "type": "deadline",
      "description": "일반 증여는 재산을 증여받은 날이 속하는 달의 말일부터 3개월 이내에 증여세를 신고·납부합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.gift.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.grant.regular.2025-income",
      "title": "2025년 귀속 근로·자녀장려금 정기신청",
      "type": "deadline",
      "description": "2025년 귀속 근로·자녀장려금 정기신청은 2026년 5월 신청 흐름으로 관리하고, 2026년에는 6월 1일까지로 기한의 특례를 반영합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.eligibility",
        "source.nts.grant.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2026-05-01",
      "end_date": "2026-06-01"
    },
    {
      "id": "deadline.grant.semiannual.2026",
      "title": "2026년 근로장려금 반기신청분 지급",
      "type": "deadline",
      "description": "2026년 상반기분은 2026년 12월 30일, 하반기분은 2027년 6월 30일 지급기한으로 관리합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2026-12-30",
      "end_date": "2027-06-30"
    },
    {
      "id": "deadline.income-tax.2025-return",
      "title": "2025년 귀속 종합소득세 확정신고",
      "type": "deadline",
      "description": "2025년 귀속 종합소득세 일반 신고·납부는 2026년 5월 1일부터 2026년 6월 1일까지입니다. 성실신고확인서 제출자는 2026년 6월 30일까지입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.income-tax.deadline"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2026-05-01",
      "end_date": "2026-06-01"
    },
    {
      "id": "deadline.inheritance.nonresident",
      "title": "상속세 비거주자 신고납부",
      "type": "deadline",
      "description": "피상속인이나 상속인 전원이 비거주자인 경우 상속개시일이 속하는 달의 말일부터 9개월 이내에 상속세를 신고·납부합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.inheritance.overview"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.inheritance.resident",
      "title": "상속세 거주자 신고납부",
      "type": "deadline",
      "description": "피상속인이 거주자인 경우 상속개시일이 속하는 달의 말일부터 6개월 이내에 상속세를 신고·납부합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.inheritance.overview"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.vat.general.first-final",
      "title": "부가가치세 일반과세자 1기 확정신고",
      "type": "deadline",
      "description": "일반과세자의 제1기 과세기간은 1월 1일부터 6월 30일까지이고, 확정신고·납부기한은 7월 1일부터 7월 25일까지입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2026-07-01",
      "end_date": "2026-07-25"
    },
    {
      "id": "deadline.vat.general.second-final",
      "title": "부가가치세 일반과세자 2기 확정신고",
      "type": "deadline",
      "description": "일반과세자의 제2기 과세기간은 7월 1일부터 12월 31일까지이고, 확정신고·납부기한은 다음 해 1월 1일부터 1월 25일까지입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2027-01-01",
      "end_date": "2027-01-25"
    },
    {
      "id": "deadline.vat.periodic",
      "title": "부가가치세 신고 납부",
      "type": "deadline",
      "description": "일반과세자는 예정·확정 신고 구조를 따르며, 2026년 세무일정상 1기 예정신고 납부는 2026년 4월 27일, 2기 예정신고 납부는 2026년 10월 26일로 관리합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty",
        "source.nts.tax-calendar.2026"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.vat.simplified.annual",
      "title": "부가가치세 간이과세자 연간 확정신고",
      "type": "deadline",
      "description": "간이과세자는 1월 1일부터 12월 31일까지를 과세기간으로 하며, 다음 해 1월 1일부터 1월 25일까지 확정신고·납부합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2027-01-01",
      "end_date": "2027-01-25"
    },
    {
      "id": "deadline.vat.simplified.preliminary",
      "title": "부가가치세 간이과세자 예정신고 예외",
      "type": "deadline",
      "description": "직전연도 공급대가 4,800만원 이상 1억400만원 미만인 간이과세자가 예정부과기간에 세금계산서를 발급한 경우 7월 1일부터 7월 25일까지 예정신고합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": "2026-07-01",
      "end_date": "2026-07-25"
    },
    {
      "id": "deadline.withholding.monthly",
      "title": "원천세 신고 납부",
      "type": "deadline",
      "description": "매월분 원천세는 다음 달 10일까지 신고·납부하는 반복 기한으로 관리합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.tax-calendar.2026"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.withholding.semiannual",
      "title": "원천세 반기별 납부",
      "type": "deadline",
      "description": "반기별 원천징수의무자는 원천징수한 소득세를 그 징수일이 속하는 반기의 마지막 달의 다음 달 10일까지 납부합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.business-income.withholding"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deadline.year-end-settlement",
      "title": "근로소득 연말정산",
      "type": "deadline",
      "description": "계속 근로자는 다음연도 2월분 근로소득 지급 시, 중도 퇴직자는 퇴직하는 달의 근로소득 지급 시 연말정산을 실시합니다.",
      "folder": "50_Deadlines",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "deadline"
      ],
      "start_date": null,
      "end_date": null
    },
    {
      "id": "deduction.credit-card-use",
      "title": "신용카드 등 사용금액",
      "type": "deduction",
      "description": "신용카드, 직불카드, 현금영수증 등 사용금액에 대한 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.deduction-limit",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.credit-card-deduction",
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "사용금액 문턱",
          "basis": "신용카드 등 사용금액",
          "condition": "총급여액의 25% 초과분",
          "rate_percent": 25,
          "note": "공제 대상 사용금액 산정 기준",
          "source": "source.nts.credit-card-deduction",
          "rate_label": "소득공제율",
          "amount_formula": "신용카드 등 사용금액 × 소득공제율 25%"
        },
        {
          "label": "신용카드 공제율",
          "basis": "신용카드 사용금액",
          "condition": "총급여 25% 초과분 중 신용카드",
          "rate_percent": 15,
          "source": "source.nts.credit-card-deduction",
          "rate_label": "소득공제율",
          "amount_formula": "신용카드 사용금액 × 소득공제율 15%"
        },
        {
          "label": "현금영수증·직불카드 공제율",
          "basis": "현금영수증·직불카드 등",
          "condition": "총급여 25% 초과분 중 현금영수증·직불카드",
          "rate_percent": 30,
          "source": "source.nts.credit-card-deduction",
          "rate_label": "소득공제율",
          "amount_formula": "현금영수증·직불카드 등 × 소득공제율 30%"
        },
        {
          "label": "전통시장·대중교통 공제율",
          "basis": "전통시장·대중교통 사용금액",
          "condition": "총급여 25% 초과분 중 전통시장·대중교통",
          "rate_percent": 40,
          "source": "source.nts.credit-card-deduction",
          "rate_label": "소득공제율",
          "amount_formula": "전통시장·대중교통 사용금액 × 소득공제율 40%"
        }
      ]
    },
    {
      "id": "deduction.employee-stock-ownership",
      "title": "우리사주조합 출연금",
      "type": "deduction",
      "description": "우리사주조합 출연금 관련 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "일반 우리사주조합 출연금",
          "basis": "우리사주조합 출연금",
          "condition": "조합원 출연금",
          "limit_krw": 4000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        },
        {
          "label": "벤처기업 우리사주조합 출연금",
          "basis": "우리사주조합 출연금",
          "condition": "벤처기업 조합원 출연금",
          "limit_krw": 15000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        }
      ]
    },
    {
      "id": "deduction.employment-maintenance-worker",
      "title": "고용유지중소기업 근로자 소득공제",
      "type": "deduction",
      "description": "고용유지 중소기업 근로자에게 적용되는 소득공제 항목입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "임금삭감액 공제",
          "basis": "고용유지 중소기업 근로자 임금삭감액",
          "condition": "고용유지 요건 충족",
          "rate_percent": 50,
          "limit_krw": 10000000,
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "deduction.health-insurance-premium",
      "title": "보험료공제",
      "type": "deduction",
      "description": "국민건강보험료, 고용보험료 등 법정 보험료 납부액을 특별소득공제로 반영하는 항목입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.special-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "국민건강보험·노인장기요양보험",
          "basis": "본인 부담 보험료",
          "condition": "근로제공기간 중 부담분",
          "benefit": "전액 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "amount_formula": "본인 부담 보험료 전액"
        },
        {
          "label": "고용보험",
          "basis": "본인 부담 보험료",
          "condition": "근로제공기간 중 부담분",
          "benefit": "전액 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "amount_formula": "본인 부담 보험료 전액"
        }
      ]
    },
    {
      "id": "deduction.housing-funds",
      "title": "주택자금공제",
      "type": "deduction",
      "description": "주택임차차입금 원리금상환액과 장기주택저당차입금 이자상환액 등 주택자금 관련 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.special-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "주택임차차입금 원리금",
          "basis": "원리금 상환액",
          "condition": "무주택 세대주 등, 국민주택규모 주택 임차",
          "rate_percent": 40,
          "limit_krw": 4000000,
          "note": "주택마련저축 공제금액과 합산 연 400만원 한도",
          "source": "source.nts.housing-rent-principal-deduction",
          "rate_label": "소득공제율"
        },
        {
          "label": "장기주택저당차입금 10년 이상",
          "basis": "이자상환액",
          "condition": "상환기간 10년 이상, 고정금리 또는 비거치식 분할상환",
          "limit_krw": 6000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상",
          "limit_krw": 8000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상 우대",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상, 고정금리 또는 비거치식 분할상환",
          "limit_krw": 18000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상 최우대",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상, 고정금리이고 비거치식 분할상환",
          "limit_krw": 20000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        }
      ]
    },
    {
      "id": "deduction.housing-savings",
      "title": "주택마련저축",
      "type": "deduction",
      "description": "청약저축, 주택청약종합저축, 근로자우대저축 등 주택마련저축 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "총급여 요건",
          "basis": "총급여액",
          "condition": "7,000만원 이하",
          "threshold_krw_max": 70000000,
          "source": "source.nts.housing-savings-deduction"
        },
        {
          "label": "납입액 공제",
          "basis": "주택마련저축 납입액",
          "condition": "연 납입액 300만원 한도",
          "threshold_krw_max": 3000000,
          "rate_percent": 40,
          "limit_krw": 1200000,
          "source": "source.nts.housing-savings-deduction",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "deduction.investment-association",
      "title": "중소기업창업투자조합 출자 등",
      "type": "deduction",
      "description": "중소기업창업투자조합 출자 등 투자 관련 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "일반 투자조합 출자",
          "basis": "출자 또는 투자금액",
          "condition": "중소기업창업투자조합 등",
          "rate_percent": 10,
          "source": "source.nts.year-end-settlement.deduction-limit",
          "rate_label": "소득공제율",
          "amount_formula": "출자 또는 투자금액 × 소득공제율 10%"
        },
        {
          "label": "벤처기업 등 3천만원 이하",
          "basis": "출자 또는 투자금액",
          "condition": "벤처기업 등 직접·간접 투자 3천만원 이하",
          "threshold_krw_max": 30000000,
          "rate_percent": 100,
          "source": "source.nts.year-end-settlement.deduction-limit",
          "rate_label": "소득공제율"
        },
        {
          "label": "벤처기업 등 3천만원 초과 5천만원 이하",
          "basis": "출자 또는 투자금액",
          "condition": "3천만원 초과 5천만원 이하",
          "threshold_krw_min": 30000000,
          "threshold_krw_max": 50000000,
          "rate_percent": 70,
          "source": "source.nts.year-end-settlement.deduction-limit",
          "rate_label": "소득공제율"
        },
        {
          "label": "벤처기업 등 5천만원 초과",
          "basis": "출자 또는 투자금액",
          "condition": "5천만원 초과",
          "threshold_krw_min": 50000000,
          "rate_percent": 30,
          "source": "source.nts.year-end-settlement.deduction-limit",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "deduction.long-term-fund",
      "title": "장기집합투자증권저축",
      "type": "deduction",
      "description": "장기집합투자증권저축에 대한 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "장기집합투자증권저축 납입액",
          "basis": "연 납입액",
          "condition": "연 600만원 한도",
          "threshold_krw_max": 6000000,
          "rate_percent": 40,
          "limit_krw": 2400000,
          "source": "source.nts.year-end-settlement.deduction-limit",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "deduction.other-income",
      "title": "그 밖의 소득공제",
      "type": "deduction",
      "description": "과세표준 계산 전 추가로 반영되는 소득공제 항목 묶음입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.income-deductions"
      ],
      "children": [
        "deduction.personal-pension-savings",
        "deduction.small-business-mutual-aid",
        "deduction.housing-savings",
        "deduction.investment-association",
        "deduction.credit-card-use",
        "deduction.employee-stock-ownership",
        "deduction.employment-maintenance-worker",
        "deduction.long-term-fund",
        "deduction.youth-long-term-fund"
      ],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.deduction-limit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit",
        "source.nts.housing-savings-deduction"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "소득공제 종합한도",
          "basis": "종합한도 적용 소득공제 합계",
          "condition": "2,500만원 초과액은 과세표준에 합산",
          "limit_krw": 25000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        },
        {
          "label": "주택자금·주택마련저축",
          "basis": "주택자금공제와 주택마련저축",
          "condition": "종합한도 적용 대상",
          "benefit": "종합한도 내 소득공제",
          "source": "source.nts.year-end-settlement.deduction-limit",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "투자·우리사주·장기저축",
          "basis": "중소기업창업투자조합 출자 등, 우리사주조합 출연금, 장기집합투자증권저축",
          "condition": "일부 벤처투자 예외를 제외하고 종합한도 적용 대상",
          "benefit": "종합한도 내 소득공제",
          "source": "source.nts.year-end-settlement.deduction-limit",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "deduction.pension-insurance",
      "title": "연금보험료공제",
      "type": "deduction",
      "description": "공적연금의 근로자 부담금을 차감소득금액 계산에 반영하는 공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.income-deductions"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "공적연금 근로자 부담금",
          "basis": "국민연금 등 공적연금보험료",
          "condition": "근로자가 부담한 공적연금보험료",
          "benefit": "전액 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "amount_formula": "국민연금 등 공적연금보험료 전액"
        }
      ]
    },
    {
      "id": "deduction.personal",
      "title": "인적공제",
      "type": "deduction",
      "description": "기본공제와 추가공제로 구성되는 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.income-deductions"
      ],
      "children": [
        "deduction.personal.basic",
        "deduction.personal.additional"
      ],
      "related": [],
      "terms": [
        "term.income-deduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "기본공제 대상자 1명당",
          "basis": "본인·배우자·부양가족",
          "condition": "기본공제 대상자",
          "deduction_krw": 1500000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "부양가족 소득요건",
          "basis": "연간 소득금액",
          "condition": "100만원 이하",
          "threshold_krw_max": 1000000,
          "note": "근로소득만 있는 경우 총급여 500만원 이하",
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "근로소득만 있는 부양가족",
          "basis": "총급여",
          "condition": "500만원 이하",
          "threshold_krw_max": 5000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "경로우대",
          "basis": "기본공제대상자",
          "condition": "70세 이상",
          "deduction_krw": 1000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "장애인",
          "basis": "기본공제대상자",
          "condition": "장애인",
          "deduction_krw": 2000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "부녀자",
          "basis": "종합소득금액",
          "condition": "3,000만원 이하 등 요건 충족",
          "threshold_krw_max": 30000000,
          "deduction_krw": 500000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "한부모",
          "basis": "배우자가 없는 기본공제대상자",
          "condition": "기본공제대상 직계비속 또는 입양자 있음",
          "deduction_krw": 1000000,
          "note": "부녀자공제와 중복 시 한부모공제 적용",
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "deduction.personal-pension-savings",
      "title": "개인연금저축 소득공제",
      "type": "deduction",
      "description": "연금저축 세액공제와 구분되는 개인연금저축 관련 소득공제 항목입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "개인연금저축 납입액",
          "basis": "2000.12.31. 이전 가입 개인연금저축",
          "condition": "연 납입액의 40%",
          "rate_percent": 40,
          "limit_krw": 720000,
          "note": "연 180만원 납입 기준 최대 72만원 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "deduction.personal.additional",
      "title": "추가공제",
      "type": "deduction",
      "description": "경로우대, 장애인, 부녀자, 한부모 등 추가 요건에 따른 인적공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.personal"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "경로우대",
          "basis": "기본공제대상자",
          "condition": "70세 이상",
          "deduction_krw": 1000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "장애인",
          "basis": "기본공제대상자",
          "condition": "장애인",
          "deduction_krw": 2000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "부녀자",
          "basis": "종합소득금액",
          "condition": "3,000만원 이하 등 요건 충족",
          "threshold_krw_max": 30000000,
          "deduction_krw": 500000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "한부모",
          "basis": "배우자가 없는 기본공제대상자",
          "condition": "기본공제대상 직계비속 또는 입양자 있음",
          "deduction_krw": 1000000,
          "note": "부녀자공제와 중복 시 한부모공제 적용",
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "deduction.personal.basic",
      "title": "기본공제",
      "type": "deduction",
      "description": "본인, 배우자, 부양가족 등 기본공제 대상자에 대한 인적공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.personal"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "기본공제 대상자 1명당",
          "basis": "본인·배우자·부양가족",
          "condition": "기본공제 대상자",
          "deduction_krw": 1500000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "부양가족 소득요건",
          "basis": "연간 소득금액",
          "condition": "100만원 이하",
          "threshold_krw_max": 1000000,
          "note": "근로소득만 있는 경우 총급여 500만원 이하",
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "근로소득만 있는 부양가족",
          "basis": "총급여",
          "condition": "500만원 이하",
          "threshold_krw_max": 5000000,
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "deduction.small-business-mutual-aid",
      "title": "소기업·소상공인 공제부금",
      "type": "deduction",
      "description": "노란우산 등 소기업·소상공인 공제부금에 대한 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "근로소득금액 4천만원 이하",
          "basis": "근로소득금액",
          "condition": "4,000만원 이하",
          "threshold_krw_max": 40000000,
          "limit_krw": 5000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        },
        {
          "label": "근로소득금액 4천만원 초과 1억원 이하",
          "basis": "근로소득금액",
          "condition": "4,000만원 초과 1억원 이하",
          "threshold_krw_min": 40000000,
          "threshold_krw_max": 100000000,
          "limit_krw": 3000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        },
        {
          "label": "근로소득금액 1억원 초과",
          "basis": "근로소득금액",
          "condition": "1억원 초과",
          "threshold_krw_min": 100000000,
          "limit_krw": 2000000,
          "source": "source.nts.year-end-settlement.deduction-limit"
        }
      ]
    },
    {
      "id": "deduction.special-income",
      "title": "특별소득공제",
      "type": "deduction",
      "description": "근로소득 연말정산 계산 구조에서 차감소득금액을 산출할 때 반영되는 특별소득공제 묶음입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.income-deductions"
      ],
      "children": [
        "deduction.health-insurance-premium",
        "deduction.housing-funds"
      ],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.deduction-limit"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.year-end-settlement.deduction-limit",
        "source.nts.housing-rent-principal-deduction",
        "source.nts.housing-mortgage-interest-deduction"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "국민건강보험·노인장기요양보험",
          "basis": "본인 부담 보험료",
          "condition": "근로제공기간 중 부담분",
          "benefit": "전액 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "amount_formula": "본인 부담 보험료 전액"
        },
        {
          "label": "고용보험",
          "basis": "본인 부담 보험료",
          "condition": "근로제공기간 중 부담분",
          "benefit": "전액 소득공제",
          "source": "source.nts.year-end-settlement.calculation",
          "amount_formula": "본인 부담 보험료 전액"
        },
        {
          "label": "주택임차차입금 원리금",
          "basis": "원리금 상환액",
          "condition": "무주택 세대주 등, 국민주택규모 주택 임차",
          "rate_percent": 40,
          "limit_krw": 4000000,
          "note": "주택마련저축 공제금액과 합산 연 400만원 한도",
          "source": "source.nts.housing-rent-principal-deduction",
          "rate_label": "소득공제율"
        },
        {
          "label": "장기주택저당차입금 10년 이상",
          "basis": "이자상환액",
          "condition": "상환기간 10년 이상, 고정금리 또는 비거치식 분할상환",
          "limit_krw": 6000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상",
          "limit_krw": 8000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상 우대",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상, 고정금리 또는 비거치식 분할상환",
          "limit_krw": 18000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        },
        {
          "label": "장기주택저당차입금 15년 이상 최우대",
          "basis": "이자상환액",
          "condition": "상환기간 15년 이상, 고정금리이고 비거치식 분할상환",
          "limit_krw": 20000000,
          "source": "source.nts.housing-mortgage-interest-deduction"
        }
      ]
    },
    {
      "id": "deduction.youth-long-term-fund",
      "title": "청년형 장기집합투자증권저축",
      "type": "deduction",
      "description": "청년형 장기집합투자증권저축에 대한 소득공제입니다.",
      "folder": "20_Deductions/IncomeDeductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "deduction.other-income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.income-deduction",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "income-deduction"
      ],
      "criteria": [
        {
          "label": "가입 소득요건",
          "basis": "총급여 또는 종합소득금액",
          "condition": "총급여 5,000만원 이하 또는 종합소득금액 3,800만원 이하",
          "threshold_krw_max": 50000000,
          "source": "source.nts.year-end-settlement.calculation"
        },
        {
          "label": "청년형 장기집합투자증권저축 납입액",
          "basis": "연 납입액",
          "condition": "연 600만원 한도",
          "threshold_krw_max": 6000000,
          "rate_percent": 40,
          "limit_krw": 2400000,
          "source": "source.nts.year-end-settlement.calculation",
          "rate_label": "소득공제율"
        }
      ]
    },
    {
      "id": "filing.business-income-withholding",
      "title": "사업소득 원천징수",
      "type": "filing",
      "description": "프리랜서 등 원천징수 대상 사업소득을 지급할 때 지급금액의 일정 비율을 원천징수하고 정해진 기한에 신고·납부하는 흐름입니다.",
      "folder": "60_Business",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.business-tax-compliance",
        "filing.withholding-tax"
      ],
      "children": [],
      "related": [
        "tax.income.comprehensive",
        "filing.withholding-tax"
      ],
      "terms": [
        "term.withholding",
        "term.withholding-obligor",
        "term.tax-rate",
        "term.deadline-special-rule"
      ],
      "deadlines": [
        "deadline.withholding.monthly",
        "deadline.withholding.semiannual"
      ],
      "sources": [
        "source.nts.business-income.withholding",
        "source.nts.withholding.overview"
      ],
      "law_reference": "",
      "tags": [
        "business-compliance"
      ],
      "criteria": [
        {
          "label": "사업소득 원천징수세율",
          "basis": "원천징수 대상 사업소득 지급금액",
          "condition": "사업소득 지급 시",
          "rate_percent": 3,
          "note": "지방소득세는 별도 확인",
          "source": "source.nts.business-income.withholding",
          "amount_formula": "원천징수 대상 사업소득 지급금액 × 적용비율 3%"
        }
      ]
    },
    {
      "id": "filing.business-registration",
      "title": "사업자등록 신청",
      "type": "filing",
      "description": "신규사업자가 사업 개시 전 또는 사업 개시일부터 20일 이내 관할 세무서장에게 등록하는 절차입니다. 일반과세자·간이과세자 유형 선택과 간이과세 배제 업종 확인을 함께 관리합니다.",
      "folder": "60_Business",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.business-tax-compliance"
      ],
      "children": [],
      "related": [
        "tax.value-added",
        "concept.general-vat-taxpayer",
        "concept.simple-vat-taxpayer",
        "filing.vat-return"
      ],
      "terms": [
        "term.general-vat-taxpayer",
        "term.simple-vat-taxpayer"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.business-registration.application"
      ],
      "law_reference": "",
      "tags": [
        "business-compliance"
      ],
      "criteria": [
        {
          "label": "사업자등록 신청기한",
          "basis": "사업 개시일",
          "condition": "사업 개시 전 또는 사업 개시일부터 20일 이내",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.business-registration.application"
        }
      ]
    },
    {
      "id": "filing.capital-gains-return",
      "title": "양도소득세 신고",
      "type": "filing",
      "description": "부동산, 주식 등 자산 양도 후 예정신고와 다음연도 확정신고 필요 여부를 구분해 관리하는 신고 절차입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar",
        "tax.income.capital-gains"
      ],
      "children": [],
      "related": [
        "tax.securities-transaction",
        "concept.capital-gains.calculation-flow",
        "concept.capital-gains.stock-basic-deduction"
      ],
      "terms": [
        "term.capital-gain",
        "term.tax-base",
        "term.deadline"
      ],
      "deadlines": [
        "deadline.capital-gains.preliminary",
        "deadline.capital-gains.final"
      ],
      "sources": [
        "source.nts.capital-gains.overview",
        "source.nts.capital-gains.deadline"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "양도소득세 예정신고",
          "basis": "양도일이 속하는 달의 말일",
          "condition": "자산 유형별 예정신고 기한 적용",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.capital-gains.deadline"
        },
        {
          "label": "양도소득세 확정신고",
          "basis": "과세기간 다음연도 5월",
          "condition": "예정신고 대상 외 확정신고 필요 여부 확인",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.capital-gains.deadline"
        }
      ]
    },
    {
      "id": "filing.gift-tax-return",
      "title": "증여세 신고",
      "type": "filing",
      "description": "증여받은 날이 속하는 달의 말일부터 일반 증여 3개월 기한을 기준으로 신고·납부를 관리하는 절차입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar",
        "tax.gift"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.donee",
        "term.tax-base",
        "term.deadline"
      ],
      "deadlines": [
        "deadline.gift.general"
      ],
      "sources": [
        "source.nts.gift.deadline"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "증여세 신고기한",
          "basis": "증여받은 날이 속하는 달의 말일",
          "condition": "일반 증여 3개월",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.gift.deadline"
        }
      ]
    },
    {
      "id": "filing.grant-application",
      "title": "근로·자녀장려금 신청",
      "type": "filing",
      "description": "국세청 근로·자녀장려금 정기·반기·기한 후 신청 및 심사 흐름입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar"
      ],
      "children": [],
      "related": [
        "support.earned-income-tax-credit",
        "support.child-tax-credit"
      ],
      "terms": [
        "term.total-income",
        "term.property-requirement"
      ],
      "deadlines": [
        "deadline.grant.regular.2025-income",
        "deadline.grant.semiannual.2026"
      ],
      "sources": [
        "source.nts.grant.eligibility",
        "source.nts.grant.deadline"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "근로·자녀장려금 정기신청",
          "basis": "2025년 귀속 소득",
          "condition": "2026년 5월 정기신청",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.grant.deadline"
        }
      ]
    },
    {
      "id": "filing.income-tax-return",
      "title": "종합소득세 확정신고",
      "type": "filing",
      "description": "종합소득이 있는 개인이 다음연도 5월 신고·납부하는 절차입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar"
      ],
      "children": [],
      "related": [
        "tax.income.comprehensive"
      ],
      "terms": [
        "term.deadline",
        "term.deadline-special-rule"
      ],
      "deadlines": [
        "deadline.income-tax.2025-return"
      ],
      "sources": [
        "source.nts.income-tax.deadline"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "확정신고 기간",
          "basis": "신고·납부기한",
          "condition": "다음연도 5월 1일부터 5월 31일까지",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.income-tax.deadline"
        }
      ]
    },
    {
      "id": "filing.inheritance-tax-return",
      "title": "상속세 신고",
      "type": "filing",
      "description": "상속개시일이 속하는 달의 말일부터 거주자 6개월, 비거주자 9개월 기한을 기준으로 신고·납부를 관리하는 절차입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar",
        "tax.inheritance"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.heir",
        "term.tax-base",
        "term.deadline"
      ],
      "deadlines": [
        "deadline.inheritance.resident",
        "deadline.inheritance.nonresident"
      ],
      "sources": [
        "source.nts.inheritance.overview"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "상속세 신고기한",
          "basis": "상속개시일이 속하는 달의 말일",
          "condition": "거주자 6개월, 비거주자 9개월",
          "amount_applicability": "정액 금액 기준 없음",
          "source": "source.nts.inheritance.overview"
        }
      ]
    },
    {
      "id": "filing.vat-return",
      "title": "부가가치세 신고 납부 절차",
      "type": "filing",
      "description": "부가가치세 과세사업자가 과세기간별 매출세액과 매입세액을 신고·납부하는 절차입니다. 일반과세자 확정신고, 간이과세자 연간 신고, 일부 간이과세자 예정신고 예외를 함께 관리합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar",
        "category.business-tax-compliance"
      ],
      "children": [],
      "related": [
        "tax.value-added",
        "concept.general-vat-taxpayer",
        "concept.simple-vat-taxpayer",
        "concept.vat-payment-exemption",
        "filing.business-registration"
      ],
      "terms": [
        "term.tax-period",
        "term.general-vat-taxpayer",
        "term.simple-vat-taxpayer",
        "term.deadline-special-rule"
      ],
      "deadlines": [
        "deadline.vat.periodic",
        "deadline.vat.general.first-final",
        "deadline.vat.general.second-final",
        "deadline.vat.simplified.annual",
        "deadline.vat.simplified.preliminary"
      ],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty",
        "source.nts.tax-calendar.2026"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "일반과세자 확정신고",
          "basis": "부가가치세 과세기간",
          "condition": "제1기·제2기 확정신고 납부",
          "amount_formula": "매출세액 - 매입세액 - 공제세액",
          "source": "source.nts.vat.filing-duty"
        },
        {
          "label": "간이과세자 연간 신고",
          "basis": "직전연도 공급대가",
          "condition": "간이과세자 과세기간 신고",
          "amount_formula": "매출액 × 업종별 부가가치율 × 10% - 공제세액",
          "source": "source.nts.vat.filing-duty"
        }
      ]
    },
    {
      "id": "filing.withholding-tax",
      "title": "원천세 신고 납부 절차",
      "type": "filing",
      "description": "원천징수의무자가 원천징수한 세액을 신고·납부하는 절차입니다. 매월 납부와 반기별 납부를 모두 연결해 급여·사업소득 지급자의 반복 업무로 관리합니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar",
        "category.business-tax-compliance"
      ],
      "children": [
        "filing.business-income-withholding"
      ],
      "related": [
        "filing.business-income-withholding"
      ],
      "terms": [
        "term.withholding",
        "term.withholding-obligor",
        "term.deadline-special-rule"
      ],
      "deadlines": [
        "deadline.withholding.monthly",
        "deadline.withholding.semiannual"
      ],
      "sources": [
        "source.nts.tax-calendar.2026",
        "source.nts.withholding.overview",
        "source.nts.business-income.withholding"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "원천세 월별 납부",
          "basis": "원천징수일",
          "condition": "징수일이 속하는 달의 다음달 10일까지",
          "amount_formula": "원천징수 대상 지급액 × 소득별 원천징수세율",
          "source": "source.nts.withholding.overview"
        }
      ]
    },
    {
      "id": "filing.year-end-settlement",
      "title": "연말정산",
      "type": "filing",
      "description": "원천징수의무자가 근로자의 해당 과세기간 근로소득세를 확정하는 절차입니다.",
      "folder": "50_Deadlines",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.filing-calendar"
      ],
      "children": [],
      "related": [
        "category.deductions-and-reliefs"
      ],
      "terms": [
        "term.withholding",
        "term.income-deduction",
        "term.tax-credit"
      ],
      "deadlines": [
        "deadline.year-end-settlement"
      ],
      "sources": [
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "연말정산 계산",
          "basis": "근로소득세 확정 절차",
          "condition": "원천징수의무자가 해당 과세기간 근로소득세를 정산",
          "amount_formula": "결정세액 - 기납부세액",
          "source": "source.nts.year-end-settlement.calculation"
        }
      ]
    },
    {
      "id": "kr-tax-system",
      "title": "OpenTax",
      "type": "domain",
      "description": "대한민국의 세금, 공제, 감면, 정책지원금, 신고·납부 기한을 Obsidian 지식 그래프로 학습하기 위한 OpenTax 최상위 항목입니다.",
      "folder": "00_Index",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [
        "category.national-taxes",
        "category.customs",
        "category.local-taxes",
        "category.deductions-and-reliefs",
        "category.policy-supports",
        "category.business-tax-compliance",
        "category.filing-calendar"
      ],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.local-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.local-tax-framework-act.2026.article8"
      ],
      "law_reference": "",
      "tags": [
        "root"
      ]
    },
    {
      "id": "local.acquisition",
      "title": "취득세",
      "type": "tax",
      "description": "부동산, 차량 등 과세물건 취득에 대해 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "취득세 산식",
          "basis": "취득가액 또는 시가표준액",
          "condition": "부동산·차량 등 과세물건 취득",
          "amount_formula": "과세표준 × 과세대상별 취득세율",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.automobile",
      "title": "자동차세",
      "type": "tax",
      "description": "자동차 보유 또는 주행 등에 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "자동차세 산식",
          "basis": "차종·용도·배기량 또는 적재량",
          "condition": "자동차 보유",
          "amount_formula": "차종별 과세단위 × 지방세법상 단위세액",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.leisure",
      "title": "레저세",
      "type": "tax",
      "description": "경륜·경정·경마 등 승자투표권 발매 등에 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "레저세 세율",
          "basis": "승자투표권·승마투표권 발매금 총액",
          "condition": "경륜·경정·경마 등",
          "rate_percent": 10,
          "amount_formula": "발매금 총액 × 10%",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.local-consumption",
      "title": "지방소비세",
      "type": "tax",
      "description": "부가가치세와 연결되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [
        "tax.value-added"
      ],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "지방소비세 산식",
          "basis": "부가가치세액",
          "condition": "부가가치세와 연동",
          "amount_formula": "부가가치세액 × 지방세법상 지방소비세율",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.local-education",
      "title": "지방교육세",
      "type": "tax",
      "description": "지방교육재정 확충을 위해 다른 지방세에 부가되는 지방 목적세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-purpose-taxes"
      ],
      "children": [],
      "related": [
        "tax.education"
      ],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "지방교육세 부가 과세",
          "basis": "취득세액·등록면허세액·레저세액 등",
          "condition": "지방교육재정 확충 목적",
          "amount_formula": "본세액 × 지방교육세율",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.local-income",
      "title": "지방소득세",
      "type": "tax",
      "description": "소득세·법인세 과세표준이 되는 소득과 연결되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [
        "tax.income",
        "tax.corporate"
      ],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "지방소득세 산식",
          "basis": "개인·법인 소득 과세표준",
          "condition": "소득세·법인세와 연결",
          "amount_formula": "지방소득세 과세표준 × 지방세법상 세율",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.property",
      "title": "재산세",
      "type": "tax",
      "description": "토지, 건축물, 주택 등 재산 보유에 대해 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [
        "tax.comprehensive-real-estate",
        "concept.cre-tax-base-date",
        "concept.cre-deduction-thresholds"
      ],
      "terms": [
        "term.local-tax",
        "term.publicly-notified-price",
        "term.tax-rate"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.nts.real-estate-tax.faq"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "주택 6천만원 이하",
          "basis": "재산세 과세표준",
          "condition": "주택 6천만원 이하",
          "threshold_krw_max": 60000000,
          "rate_percent": 0.1,
          "progressive_deduction_krw": 0,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "주택 1억5천만원 이하",
          "basis": "재산세 과세표준",
          "condition": "주택 1억5천만원 이하",
          "threshold_krw_max": 150000000,
          "rate_percent": 0.15,
          "progressive_deduction_krw": 30000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "주택 3억원 이하",
          "basis": "재산세 과세표준",
          "condition": "주택 3억원 이하",
          "threshold_krw_max": 300000000,
          "rate_percent": 0.25,
          "progressive_deduction_krw": 180000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "주택 3억원 초과",
          "basis": "재산세 과세표준",
          "condition": "주택 3억원 초과",
          "threshold_krw_min": 300000000,
          "rate_percent": 0.4,
          "progressive_deduction_krw": 630000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "종합합산 5천만원 이하",
          "basis": "재산세 과세표준",
          "condition": "종합합산 5천만원 이하",
          "threshold_krw_max": 50000000,
          "rate_percent": 0.2,
          "progressive_deduction_krw": 0,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "종합합산 1억원 이하",
          "basis": "재산세 과세표준",
          "condition": "종합합산 1억원 이하",
          "threshold_krw_max": 100000000,
          "rate_percent": 0.3,
          "progressive_deduction_krw": 50000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "종합합산 1억원 초과",
          "basis": "재산세 과세표준",
          "condition": "종합합산 1억원 초과",
          "threshold_krw_min": 100000000,
          "rate_percent": 0.5,
          "progressive_deduction_krw": 250000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "별도합산 2억원 이하",
          "basis": "재산세 과세표준",
          "condition": "별도합산 2억원 이하",
          "threshold_krw_max": 200000000,
          "rate_percent": 0.2,
          "progressive_deduction_krw": 0,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "별도합산 10억원 이하",
          "basis": "재산세 과세표준",
          "condition": "별도합산 10억원 이하",
          "threshold_krw_max": 1000000000,
          "rate_percent": 0.3,
          "progressive_deduction_krw": 200000,
          "source": "source.nts.real-estate-tax.faq"
        },
        {
          "label": "별도합산 10억원 초과",
          "basis": "재산세 과세표준",
          "condition": "별도합산 10억원 초과",
          "threshold_krw_min": 1000000000,
          "rate_percent": 0.4,
          "progressive_deduction_krw": 1200000,
          "source": "source.nts.real-estate-tax.faq"
        }
      ]
    },
    {
      "id": "local.regional-resource-facility",
      "title": "지역자원시설세",
      "type": "tax",
      "description": "지역자원 보호, 안전관리 등 특정 재원 목적의 지방 목적세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-purpose-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "지역자원시설세 산식",
          "basis": "특정자원·특정부동산·소방분 과세표준",
          "condition": "지역자원 보호 또는 소방시설 재원 목적",
          "amount_formula": "과세대상별 과세표준 × 지방세법상 세율 또는 정액세",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.registration-license",
      "title": "등록면허세",
      "type": "tax",
      "description": "재산권 등 등록 또는 각종 면허에 대해 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "등록면허세 산식",
          "basis": "등록가액 또는 면허 종류",
          "condition": "등기·등록 또는 면허",
          "amount_formula": "등록가액 × 등록세율 또는 면허종별 정액세",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.resident",
      "title": "주민세",
      "type": "tax",
      "description": "개인, 사업소, 종업원 등 지역 구성원에게 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "주민세 산식",
          "basis": "개인분·사업소분·종업원분 과세표준",
          "condition": "지방자치단체 조례와 지방세법 기준 적용",
          "amount_formula": "개인분 정액세 또는 사업소 연면적·종업원 급여총액 기준 산식",
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "local.tobacco-consumption",
      "title": "담배소비세",
      "type": "tax",
      "description": "담배 반출 또는 반입에 대해 과세되는 지방 보통세입니다.",
      "folder": "10_Taxes/Local",
      "basis_year": 2026,
      "effective_date": "2026-02-05",
      "expiration_date": null,
      "parents": [
        "category.local-ordinary-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.local-tax"
      ],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8",
        "source.law.local-tax-act.rates"
      ],
      "law_reference": "지방세기본법 제8조",
      "tags": [
        "local-tax"
      ],
      "criteria": [
        {
          "label": "궐련 담배소비세",
          "basis": "궐련 20개비",
          "condition": "궐련 담배 반출 또는 반입",
          "amount_krw": 1007,
          "source": "source.law.local-tax-act.rates"
        }
      ]
    },
    {
      "id": "reduction.good-landlord",
      "title": "착한임대인 세액공제 제도",
      "type": "tax-reduction",
      "description": "상가건물 임대료 인하액에 적용되는 세액공제 제도입니다.",
      "folder": "20_Deductions/TaxReductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-reductions"
      ],
      "children": [],
      "related": [
        "corporate.support.good-landlord-credit"
      ],
      "terms": [
        "term.tax-credit",
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "임대료 인하액",
          "basis": "상가건물 임대료 인하액",
          "condition": "소상공인 임차인 임대료 인하 등 요건 충족",
          "rate_percent": 70,
          "rate_label": "세액공제율",
          "note": "요건과 과세연도별 적용기한 확인 필요",
          "source": "source.nts.corporate-tax.reliefs",
          "amount_formula": "상가건물 임대료 인하액 × 세액공제율 70%"
        }
      ]
    },
    {
      "id": "reduction.sme-employment-income",
      "title": "중소기업 취업자 소득세 감면",
      "type": "tax-reduction",
      "description": "청년 등 중소기업 취업자의 소득세를 일정 요건에서 감면하는 항목입니다.",
      "folder": "20_Deductions/TaxReductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-reductions"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.sme-employment-income-reduction"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "청년",
          "basis": "중소기업 취업자 근로소득세",
          "condition": "근로계약 체결일 현재 15~34세 이하",
          "rate_percent": 90,
          "rate_label": "감면율",
          "limit_krw": 2000000,
          "note": "감면기간 5년",
          "source": "source.nts.sme-employment-income-reduction"
        },
        {
          "label": "고령자",
          "basis": "중소기업 취업자 근로소득세",
          "condition": "근로계약 체결일 현재 60세 이상",
          "rate_percent": 70,
          "rate_label": "감면율",
          "limit_krw": 2000000,
          "note": "감면기간 3년",
          "source": "source.nts.sme-employment-income-reduction"
        },
        {
          "label": "장애인·경력단절근로자",
          "basis": "중소기업 취업자 근로소득세",
          "condition": "장애인 또는 경력단절근로자 요건 충족",
          "rate_percent": 70,
          "rate_label": "감면율",
          "limit_krw": 2000000,
          "note": "감면기간 3년",
          "source": "source.nts.sme-employment-income-reduction"
        }
      ]
    },
    {
      "id": "reduction.sme-special",
      "title": "중소기업특별세액감면",
      "type": "tax-reduction",
      "description": "제조업 등 일정 업종 중소기업 소득에 대한 세액감면입니다.",
      "folder": "20_Deductions/TaxReductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-reductions"
      ],
      "children": [],
      "related": [
        "corporate.support.sme-special-reduction"
      ],
      "terms": [
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs",
        "source.nts.corporate-tax-consulting.2026"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "소기업 수도권 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "소기업, 수도권 내 제조업·출판업 등",
          "rate_percent": 20,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 20%"
        },
        {
          "label": "소기업 수도권 외 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "소기업, 수도권 외 제조업·출판업 등",
          "rate_percent": 30,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 30%"
        },
        {
          "label": "중기업 수도권 외 제조업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "중기업, 수도권 외 제조업 등",
          "rate_percent": 15,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 15%"
        },
        {
          "label": "도소매·의료업 등",
          "basis": "중소기업 특별세액감면",
          "condition": "업종·지역별 차등",
          "rate_percent_min": 5,
          "rate_percent_max": 10,
          "rate_label": "감면율",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "중소기업 특별세액감면 × 감면율 5%~10%"
        }
      ]
    },
    {
      "id": "reduction.startup-sme",
      "title": "창업중소기업 등에 대한 세액감면",
      "type": "tax-reduction",
      "description": "창업중소기업 등의 최초 소득발생 과세연도와 이후 일정 기간에 적용되는 세액감면입니다.",
      "folder": "20_Deductions/TaxReductions",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.tax-reductions"
      ],
      "children": [],
      "related": [
        "corporate.support.startup-sme-reduction"
      ],
      "terms": [
        "term.tax-reduction"
      ],
      "deadlines": [],
      "sources": [
        "source.nts.corporate-tax.reliefs",
        "source.nts.corporate-tax-consulting.2026"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "2026년 이후 일반 창업중소기업",
          "basis": "법인세 또는 소득세",
          "condition": "수도권 외 지역 또는 수도권 인구감소지역",
          "rate_percent": 50,
          "rate_label": "감면율",
          "note": "최초 소득발생 과세연도와 이후 4년",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "법인세 또는 소득세 × 감면율 50%"
        },
        {
          "label": "2026년 이후 청년·생계형 창업",
          "basis": "법인세 또는 소득세",
          "condition": "수도권 외 지역 또는 수도권과밀억제권역 외",
          "rate_percent": 100,
          "rate_label": "감면율",
          "note": "수도권 과밀억제권역 50%, 수도권 75% 등 지역별 차등",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "법인세 또는 소득세 × 감면율 100%"
        },
        {
          "label": "상시근로자 증가 추가감면",
          "basis": "상시근로자 증가율",
          "condition": "고용 증가 요건 충족",
          "rate_percent": 100,
          "rate_label": "추가감면 산식",
          "note": "상시근로자 증가율 × 100%",
          "source": "source.nts.corporate-tax-consulting.2026",
          "amount_formula": "상시근로자 증가율 × 추가감면 산식 100%"
        }
      ]
    },
    {
      "id": "source.ccrs.long-term-delinquent-debt-adjustment",
      "title": "장기연체자 특별채무조정",
      "type": "source",
      "description": "새도약기금 관련 5년 이상 장기연체채권 특별채무조정의 2026년 기준중위소득 125%, 채무감면, 분할상환, 상환유예 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "신용회복위원회"
      ],
      "publisher": "신용회복위원회",
      "url": "https://ad.ccrs.or.kr/cms/com/index.do?CONTENTS_NO=2&MENU_ID=1580",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.customs-act.2026.article14",
      "title": "관세법 제14조",
      "type": "source",
      "description": "수입물품에 관세를 부과한다는 관세의 과세물건 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900015991",
      "basis_date": "시행 2026-01-01"
    },
    {
      "id": "source.fsc.isa.policy",
      "title": "ISA 정책문답",
      "type": "source",
      "description": "개인종합자산관리계좌(ISA)의 연 2,000만원 납입한도, 순소득 200만원 비과세, 초과분 분리과세 등 세제지원과 가입 제한을 이해하기 위한 정책 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "금융위원회"
      ],
      "publisher": "금융위원회",
      "url": "https://www.fsc.go.kr/po020201/27339",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.fsc.youth-future-savings",
      "title": "청년미래적금 카드뉴스",
      "type": "source",
      "description": "2026년 6월 출시 예정 청년미래적금의 가입 소득기준, 만기, 월 납입한도, 정부기여금 매칭비율, 비과세 특례 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "금융위원회"
      ],
      "publisher": "금융위원회",
      "url": "https://www.fsc.go.kr/no040101?cnId=2983",
      "basis_date": "2025-12-11"
    },
    {
      "id": "source.govkr.basic-livelihood-benefit",
      "title": "생계급여",
      "type": "source",
      "description": "2026년 생계급여 선정·급여기준, 기준 중위소득 32%, 가구원 수별 급여기준, 부양의무자 제외 기준 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "정부24"
      ],
      "publisher": "정부24",
      "url": "https://www.gov.kr/portal/service/serviceInfo/WII000001410",
      "basis_date": "최종수정일 2026-02-09"
    },
    {
      "id": "source.hf.didimdol-loan",
      "title": "내집마련 디딤돌대출 상품소개",
      "type": "source",
      "description": "디딤돌대출의 무주택, 순자산, 주택가격, 부부합산 연소득, LTV·DTI, 대출한도 기준 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "한국주택금융공사"
      ],
      "publisher": "한국주택금융공사",
      "url": "https://www.hf.go.kr/ko/sub01/sub01_02_01.do",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.hf.didimdol-rate.2026-05",
      "title": "2026년 5월 디딤돌대출 금리안내",
      "type": "source",
      "description": "2026년 5월 기준 디딤돌대출 소득구간별 만기 금리와 우대금리 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "한국주택금융공사"
      ],
      "publisher": "한국주택금융공사",
      "url": "https://hf.go.kr/ko/sub01/sub01_02_03.do",
      "basis_date": "공시일 2026-05-01"
    },
    {
      "id": "source.hf.special-rent-guarantee",
      "title": "특례전세자금보증",
      "type": "source",
      "description": "무주택 청년, 다자녀가구, 정책서민금융 이용자 등 특례전세자금보증 대상별 보증요건과 보증한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "한국주택금융공사"
      ],
      "publisher": "한국주택금융공사",
      "url": "https://www.hf.go.kr/ko/sub02/sub02_01_04.do",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.kinfa.hessal-119",
      "title": "햇살론119",
      "type": "source",
      "description": "은행권 채무조정 프로그램을 성실상환 중인 영세 개인사업자 대상 신규 운전자금 보증부 대출의 지원요건과 한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "서민금융진흥원"
      ],
      "publisher": "서민금융진흥원",
      "url": "https://www.kinfa.or.kr/financialProduct/hessalLoanEmergency.do",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.kinfa.hessal-loan-youth",
      "title": "햇살론유스",
      "type": "source",
      "description": "만 19~34세 청년·대학생·사회초년생 대상 햇살론유스의 소득요건, 동일인 한도, 연간·용도별 보증한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "서민금융진흥원"
      ],
      "publisher": "서민금융진흥원",
      "url": "https://www.kinfa.or.kr/financialProduct/hessalLoanYoos.do",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.kinfa.illegal-private-finance-prevention-loan",
      "title": "불법사금융예방대출",
      "type": "source",
      "description": "신용평점 하위 20%·연소득 3,500만원 이하 대상 생계비 정책서민금융상품의 대출한도, 금리, 상환방식 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "서민금융진흥원"
      ],
      "publisher": "서민금융진흥원",
      "url": "https://www.kinfa.or.kr/financialProduct/smallLivingLoan.do",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.kinfa.youth-leap",
      "title": "청년도약계좌 상품 안내",
      "type": "source",
      "description": "청년도약계좌 가입 연령, 개인소득, 가구소득, 금융소득종합과세 이력 제한 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "서민금융진흥원"
      ],
      "publisher": "서민금융진흥원",
      "url": "https://ylaccount.kinfa.or.kr/main",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.law.customs-tariff",
      "title": "관세법 관세율표",
      "type": "source",
      "description": "수입물품 품목분류별 관세율표와 품목별 세율 적용 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/관세법/별표",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.education-tax-act.article5",
      "title": "교육세법 제5조",
      "type": "source",
      "description": "교육세 과세표준과 세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/교육세법/제5조",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.individual-consumption-tax-act.rates",
      "title": "개별소비세법 세율 조문",
      "type": "source",
      "description": "과세물품, 과세장소, 과세유흥장소, 영업행위별 개별소비세 세율과 정액세 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/개별소비세법",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.liquor-tax-act.rates",
      "title": "주세법 세율 조문",
      "type": "source",
      "description": "주류 종류별 주세 종가세·종량세 세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/주세법",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.local-tax-act.rates",
      "title": "지방세법 세율 조문",
      "type": "source",
      "description": "취득세, 등록면허세, 레저세, 담배소비세, 지방소비세, 주민세, 지방소득세, 자동차세, 지역자원시설세, 지방교육세의 세율·세액 산식 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/지방세법",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.securities-transaction-tax-act.article8",
      "title": "증권거래세법 제8조",
      "type": "source",
      "description": "주권 양도 시 증권거래세 과세표준과 세율 적용 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/증권거래세법/제8조",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.special-rural-development-tax-act.article5",
      "title": "농어촌특별세법 제5조",
      "type": "source",
      "description": "농어촌특별세 과세표준과 세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/농어촌특별세법/제5조",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.stamp-tax-act.article3",
      "title": "인지세법 제3조",
      "type": "source",
      "description": "과세문서와 문서 기재금액별 인지세액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/인지세법/제3조",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.law.transport-energy-environment-tax-act.rates",
      "title": "교통·에너지·환경세법 세율 조문",
      "type": "source",
      "description": "휘발유, 경유 등 과세물품별 교통·에너지·환경세 정액세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/법령/교통ㆍ에너지ㆍ환경세법",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.local-tax-framework-act.2026.article8",
      "title": "지방세기본법 제8조",
      "type": "source",
      "description": "특별시세, 광역시세, 도세, 구세, 시·군세, 특별자치시·특별자치도세의 세목 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000903169",
      "basis_date": "시행 2026-02-05"
    },
    {
      "id": "source.moef.isa.tax-benefit",
      "title": "ISA 세제혜택 설명",
      "type": "source",
      "description": "ISA 계좌 순소득 200만원, 서민·농어민형 400만원 비과세와 초과분 9% 저율 분리과세 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "기획재정부·대한민국 정책브리핑"
      ],
      "publisher": "기획재정부·대한민국 정책브리핑",
      "url": "https://www.korea.kr/briefing/actuallyView.do?newsId=148874193",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.national-tax-framework-act.2026.article2",
      "title": "국세기본법 제2조",
      "type": "source",
      "description": "국세 세목, 세법, 원천징수, 과세기간, 과세표준 등 국세 기본 용어의 법률상 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국가법령정보센터"
      ],
      "publisher": "국가법령정보센터",
      "url": "https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=900637068",
      "basis_date": "시행 2026-01-01"
    },
    {
      "id": "source.nts.business-income.withholding",
      "title": "사업소득 원천징수",
      "type": "source",
      "description": "원천징수 대상 사업소득, 3% 원천징수, 다음 달 10일 또는 반기 마지막 달 다음 달 10일 납부 흐름 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7902&mi=6466",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.business-registration.application",
      "title": "사업자등록 신청",
      "type": "source",
      "description": "신규사업자 사업자등록, 일반과세자·간이과세자 유형 선택, 간이과세 배제 업종 확인 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7777&mi=2444",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.capital-gains.basic-deduction",
      "title": "양도소득 기본공제 신고서식",
      "type": "source",
      "description": "양도소득기본공제가 국내 부동산, 국내 주식 등, 국외 부동산, 국외 주식 등, 파생상품별로 각각 2,500,000원 적용된다는 신고서식 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/tax/sub/1.2.3.%EC%96%91%EB%8F%84%EC%86%8C%EB%93%9D%EA%B3%BC%EC%84%B8%ED%91%9C%EC%A4%80%20%EC%8B%A0%EA%B3%A0%20%EB%B0%8F%20%EB%82%A9%EB%B6%80%EA%B3%84%EC%82%B0%EC%84%9C.html",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.capital-gains.deadline",
      "title": "양도소득세 신고납부기한",
      "type": "source",
      "description": "토지·건물·부동산 권리·기타자산, 주식·출자지분 양도의 예정신고와 다음연도 5월 확정신고 기한 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7713&mi=2371",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.capital-gains.overview",
      "title": "양도소득세 개요",
      "type": "source",
      "description": "양도소득세 세액계산 흐름, 부동산·주식 양도차익 계산, 기본공제와 가산세 흐름 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7709&mi=2308",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.capital-gains.rates",
      "title": "양도소득세 세율",
      "type": "source",
      "description": "양도소득세 기본세율, 보유기간·자산 유형별 세율, 국외주식·파생상품 세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7711&mi=2312",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.comprehensive-real-estate.overview",
      "title": "종합부동산세 개요",
      "type": "source",
      "description": "매년 6월 1일 과세기준일, 주택·종합합산토지·별도합산토지 공제금액과 재산세-종합부동산세 연결 구조 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7733&mi=2351",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.comprehensive-real-estate.rates",
      "title": "종합부동산세 세율",
      "type": "source",
      "description": "2023년 이후 주택, 종합합산토지, 별도합산토지의 종합부동산세 과세표준 구간별 세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7736&mi=40378",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.corporate-tax-consulting.2026",
      "title": "중소기업 공제·감면 컨설팅 제도 안내",
      "type": "source",
      "description": "2026년 창업중소기업 세액감면, 중소기업특별세액감면, 통합투자세액공제 등 주요 공제·감면율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239070&mi=41093",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.corporate-tax.rates",
      "title": "법인세 세율",
      "type": "source",
      "description": "2026.1.1. 이후 개시 사업연도 법인세 각 사업연도 소득 과세표준 구간, 세율, 누진공제액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7746",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.corporate-tax.reliefs",
      "title": "법인세 공제감면",
      "type": "source",
      "description": "중소기업, 모든 기업, 법인세법상 공제·감면과 과세이연 지원제도의 공식 목록 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7987&mi=6561",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.credit-card-deduction",
      "title": "신용카드 등 사용금액 소득공제",
      "type": "source",
      "description": "신용카드, 직불카드, 현금영수증 사용액 소득공제와 총급여 25% 기준의 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7794&mi=2202",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.ctc.intro",
      "title": "자녀장려금 소개",
      "type": "source",
      "description": "자녀장려금의 부양자녀, 총소득, 자녀 1인당 지급액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7782&mi=2451",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.donation-credit",
      "title": "기부금 세액공제",
      "type": "source",
      "description": "정치자금, 고향사랑, 특례, 우리사주조합, 일반기부금의 공제율과 금액 구간 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239040&mi=40978",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.education-expense-credit",
      "title": "교육비 세액공제",
      "type": "source",
      "description": "교육비 세액공제의 본인 전액, 취학전·초중고 300만원, 대학생 900만원, 장애인 특수교육비 전액 한도와 15% 공제율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239024&mi=40612",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.eitc.intro",
      "title": "근로장려금 소개",
      "type": "source",
      "description": "근로장려금 제도 취지, 가구 유형별 소득 기준, 최대지급액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7781&mi=2450",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.gift.deadline",
      "title": "증여세 신고납부기한",
      "type": "source",
      "description": "일반 증여와 증여의제 유형별 법정신고기한과 증여세 신고 제출서류 흐름 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7727&mi=2339",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.gift.rates",
      "title": "증여세 세율",
      "type": "source",
      "description": "증여세 과세표준 5단계 초과누진세율, 세대생략 할증, 창업자금·가업승계 특례세율 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7960&mi=2227",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.grant.2026-regular-press",
      "title": "2026년 근로·자녀장려금 정기신청 보도자료",
      "type": "source",
      "description": "2025년 귀속 근로·자녀장려금 소득요건, 재산요건, 감액구간, 정기 신청·지급 일정 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/na/ntt/selectNttInfo.do?mi=2201&nttSn=1350768",
      "basis_date": "2026-04-30"
    },
    {
      "id": "source.nts.grant.deadline",
      "title": "근로·자녀장려금 심사 및 지급",
      "type": "source",
      "description": "정기신청분, 기한 후 신청분, 반기신청분의 심사와 지급기한 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7784&mi=2453",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.grant.eligibility",
      "title": "근로·자녀장려금 신청자격",
      "type": "source",
      "description": "2025년 소득요건, 2025년 6월 1일 재산요건, 신청제외자 기준의 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7783&mi=2452",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.housing-mortgage-interest-deduction",
      "title": "장기주택저당차입금 이자상환액 소득공제",
      "type": "source",
      "description": "장기주택저당차입금 이자상환액의 상환기간·상환방식별 600만원~2,000만원 한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239020&mi=40630",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.housing-rent-principal-deduction",
      "title": "주택임차차입금 원리금 상환액 소득공제",
      "type": "source",
      "description": "주택임차차입금 원리금 상환액의 공제대상자, 주택요건, 40% 공제율, 연 400만원 한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239021&mi=40629",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.housing-savings-deduction",
      "title": "주택마련저축 소득공제",
      "type": "source",
      "description": "총급여 7,000만원 이하 무주택 세대주·배우자의 주택마련저축 납입액 40%, 연 납입액 300만원 한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239022&mi=40610",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.income-tax.deadline",
      "title": "종합소득세 신고납부기한",
      "type": "source",
      "description": "2025년 귀속 종합소득세 신고·납부 기한과 기한의 특례 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7665&mi=2225",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.income-tax.rates",
      "title": "종합소득세 세율",
      "type": "source",
      "description": "2023~2025년 귀속 종합소득세 과세표준 구간, 세율, 누진공제액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7667&mi=2223",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.inheritance.overview",
      "title": "상속세 개요",
      "type": "source",
      "description": "상속세 신고납부기한, 거주자 6개월·비거주자 9개월 기한과 제출서류 흐름 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7719&mi=2324",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.inheritance.rates",
      "title": "상속세 세율",
      "type": "source",
      "description": "상속세 과세표준 5단계 초과누진세율과 누진공제액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7957&mi=6529",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.monthly-rent-credit",
      "title": "월세액 세액공제",
      "type": "source",
      "description": "월세액 세액공제의 총급여, 종합소득금액, 주택, 전입신고, 한도 조건 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239025",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.real-estate-tax.faq",
      "title": "궁금해요 종합부동산 세법",
      "type": "source",
      "description": "종합부동산세 과세표준 계산식, 공정시장가액비율, 재산세 표준세율, 세액공제와 세부담상한 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7739&mi=2357",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.retirement-income.calculation",
      "title": "퇴직소득세 계산방법",
      "type": "source",
      "description": "퇴직소득금액, 근속연수공제, 환산급여, 환산급여공제, 과세표준, 환산산출세액, 산출세액 계산 구조와 근속연수별 공제금액 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7880&mi=6444",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.sme-employment-income-reduction",
      "title": "중소기업 취업자 소득세 감면",
      "type": "source",
      "description": "청년, 고령자, 장애인, 경력단절근로자별 감면기간, 감면율, 과세기간별 200만원 감면한도 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=239023&mi=40611",
      "basis_date": "2026-05-03 확인"
    },
    {
      "id": "source.nts.tax-calendar.2026",
      "title": "2026년 국세청 세무일정",
      "type": "source",
      "description": "월별 신고·납부 일정과 기한의 특례 확인용 공식 일정입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/ad/taxSchdul/selectList.do?mi=135747&taxYear=2026",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.vat.filing-duty",
      "title": "부가가치세 신고·납부 의무",
      "type": "source",
      "description": "일반과세자와 간이과세자의 과세기간, 확정신고 납부기한, 간이과세자 예정신고 및 납부면제 기준 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7806",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.vat.overview",
      "title": "부가가치세 개요",
      "type": "source",
      "description": "부가가치세 구조와 일반과세자·간이과세자 구분 기준의 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7693&mi=2272",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.withholding.overview",
      "title": "원천징수 개요",
      "type": "source",
      "description": "원천징수 제도, 원천징수의무자, 원천징수세액 납세지와 신고·납부 흐름 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7701&mi=2289",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.year-end-settlement.calculation",
      "title": "연말정산 세액계산방법",
      "type": "source",
      "description": "연말정산 계산 단계와 인적공제, 연금보험료공제, 특별소득공제, 세액감면, 세액공제의 구조 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7870&mi=2312",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.year-end-settlement.deduction-limit",
      "title": "근로소득 과세표준과 산출세액",
      "type": "source",
      "description": "소득공제 종합한도와 종합한도 적용 특별소득공제 등 항목의 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7873&mi=6594",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "source.nts.year-end-settlement.special-credit",
      "title": "근로소득 특별세액공제",
      "type": "source",
      "description": "보험료, 의료비, 교육비, 기부금 등 특별세액공제 항목의 근거입니다.",
      "folder": "90_Sources",
      "basis_year": null,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [],
      "law_reference": "",
      "tags": [
        "official-source",
        "국세청"
      ],
      "publisher": "국세청",
      "url": "https://kids.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7874&mi=6438",
      "basis_date": "2026-05-02 확인"
    },
    {
      "id": "support.basic-livelihood-benefit",
      "title": "생계급여",
      "type": "support-program",
      "description": "생활이 어려운 국민기초생활보장 수급자에게 최저생활 보장을 위해 현금 급여를 지급하는 정부24 복지급여입니다. 2026년 선정·급여기준은 기준 중위소득 32%입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.illegal-private-finance-prevention-loan"
      ],
      "terms": [
        "term.median-income",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.govkr.basic-livelihood-benefit"
      ],
      "law_reference": "",
      "tags": [
        "cash-support",
        "gov24",
        "welfare"
      ],
      "criteria": [
        {
          "label": "1인 가구 선정·급여기준",
          "basis": "소득인정액",
          "condition": "2026년 기준 중위소득 32% 이하",
          "threshold_krw_max": 820556,
          "benefit": "생계급여 기준액에서 소득인정액 차감 지급",
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "2인 가구 선정·급여기준",
          "basis": "소득인정액",
          "condition": "2026년 기준 중위소득 32% 이하",
          "threshold_krw_max": 1343773,
          "benefit": "생계급여 기준액에서 소득인정액 차감 지급",
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "3인 가구 선정·급여기준",
          "basis": "소득인정액",
          "condition": "2026년 기준 중위소득 32% 이하",
          "threshold_krw_max": 1714892,
          "benefit": "생계급여 기준액에서 소득인정액 차감 지급",
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "4인 가구 선정·급여기준",
          "basis": "소득인정액",
          "condition": "2026년 기준 중위소득 32% 이하",
          "threshold_krw_max": 2078316,
          "benefit": "생계급여 기준액에서 소득인정액 차감 지급",
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "5인 가구 선정·급여기준",
          "basis": "소득인정액",
          "condition": "2026년 기준 중위소득 32% 이하",
          "threshold_krw_max": 2418150,
          "benefit": "생계급여 기준액에서 소득인정액 차감 지급",
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "부양의무자 고소득 제외",
          "basis": "부양의무자 연 소득",
          "condition": "1.3억원 초과 시 제외 가능",
          "threshold_krw": 130000000,
          "source": "source.govkr.basic-livelihood-benefit"
        },
        {
          "label": "부양의무자 일반재산 제외",
          "basis": "부양의무자 일반재산",
          "condition": "12억원 초과 시 제외 가능",
          "threshold_krw": 1200000000,
          "source": "source.govkr.basic-livelihood-benefit"
        }
      ]
    },
    {
      "id": "support.child-tax-credit",
      "title": "자녀장려금",
      "type": "support-program",
      "description": "18세 미만 부양자녀가 있는 저소득 가구의 자녀양육을 지원하는 국세청 지원금입니다. 2025년 귀속 총소득 기준은 홑벌이·맞벌이 7,000만원 미만입니다.",
      "folder": "30_Supports",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "credit.child",
        "filing.grant-application"
      ],
      "terms": [
        "term.total-income",
        "term.property-requirement",
        "term.eligibility-threshold"
      ],
      "deadlines": [
        "deadline.grant.regular.2025-income"
      ],
      "sources": [
        "source.nts.ctc.intro",
        "source.nts.grant.eligibility",
        "source.nts.grant.deadline",
        "source.nts.grant.2026-regular-press"
      ],
      "law_reference": "",
      "tags": [
        "cash-support"
      ],
      "criteria": [
        {
          "label": "홑벌이·맞벌이 총소득",
          "basis": "부부합산 총소득",
          "condition": "7,000만원 미만",
          "threshold_krw_max": 70000000,
          "max_amount_krw": 1000000,
          "note": "자녀 1인당 최대 100만원, 최소 50만원",
          "source": "source.nts.ctc.intro"
        },
        {
          "label": "부양자녀",
          "basis": "자녀 연령",
          "condition": "18세 미만 부양자녀",
          "benefit": "자녀장려금 대상",
          "source": "source.nts.ctc.intro",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "재산요건",
          "basis": "가구원 전체 재산 합계액",
          "condition": "2억4천만원 미만",
          "threshold_krw_max": 240000000,
          "benefit": "신청 가능",
          "source": "source.nts.grant.2026-regular-press"
        },
        {
          "label": "재산 감액구간",
          "basis": "가구원 전체 재산 합계액",
          "condition": "1억7천만원 이상 2억4천만원 미만",
          "threshold_krw_min": 170000000,
          "threshold_krw_max": 240000000,
          "benefit": "산정액의 50% 지급",
          "source": "source.nts.grant.2026-regular-press"
        }
      ]
    },
    {
      "id": "support.didimdol-loan",
      "title": "내집마련 디딤돌대출",
      "type": "support-program",
      "description": "무주택 서민의 주택 구입자금을 낮은 금리로 공급하는 정책모기지입니다. 소득, 순자산, 주택가격, LTV·DTI, 대출한도를 함께 확인합니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "credit.monthly-rent",
        "tax.comprehensive-real-estate",
        "support.youth-special-rent-guarantee"
      ],
      "terms": [
        "term.policy-finance",
        "term.policy-loan",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.hf.didimdol-loan",
        "source.hf.didimdol-rate.2026-05"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "housing",
        "loan"
      ],
      "criteria": [
        {
          "label": "순자산",
          "basis": "본인 및 배우자 합산 순자산",
          "condition": "5.11억원 이하",
          "threshold_krw_max": 511000000,
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "주택가격",
          "basis": "공부상 주택 평가액",
          "condition": "5억원 이하",
          "threshold_krw_max": 500000000,
          "note": "신혼·2자녀 이상 가구는 6억원 이하",
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "기본 소득요건",
          "basis": "부부합산 연소득",
          "condition": "6,000만원 이하",
          "threshold_krw_max": 60000000,
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "생애최초·2자녀 이상 소득요건",
          "basis": "부부합산 연소득",
          "condition": "7,000만원 이하",
          "threshold_krw_max": 70000000,
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "신혼가구 소득요건",
          "basis": "부부합산 연소득",
          "condition": "8,500만원 이하",
          "threshold_krw_max": 85000000,
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "대출한도",
          "basis": "대출한도",
          "condition": "최대 2억원",
          "limit_krw": 200000000,
          "note": "생애최초 2.4억원, 신혼·2자녀 이상 3.2억원",
          "source": "source.hf.didimdol-loan"
        },
        {
          "label": "LTV",
          "basis": "담보인정비율",
          "condition": "최대 70%",
          "rate_percent": 70,
          "rate_label": "LTV",
          "source": "source.hf.didimdol-loan",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        },
        {
          "label": "DTI",
          "basis": "총부채상환비율",
          "condition": "최대 60%",
          "rate_percent": 60,
          "rate_label": "DTI",
          "source": "source.hf.didimdol-loan",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        },
        {
          "label": "2026년 5월 금리",
          "basis": "소득구간·만기별 금리",
          "condition": "연 2.85%~4.15%",
          "rate_percent_min": 2.85,
          "rate_percent_max": 4.15,
          "rate_label": "금리",
          "source": "source.hf.didimdol-rate.2026-05",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        }
      ]
    },
    {
      "id": "support.earned-income-tax-credit",
      "title": "근로장려금",
      "type": "support-program",
      "description": "근로·사업·종교인소득이 있는 저소득 가구의 근로를 장려하기 위해 지급하는 국세청 지원금입니다. 2025년 귀속 소득 기준은 단독 2,200만원, 홑벌이 3,200만원, 맞벌이 4,400만원 미만입니다.",
      "folder": "30_Supports",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "tax.income.comprehensive",
        "filing.grant-application"
      ],
      "terms": [
        "term.total-income",
        "term.gross-pay",
        "term.property-requirement",
        "term.eligibility-threshold"
      ],
      "deadlines": [
        "deadline.grant.regular.2025-income",
        "deadline.grant.semiannual.2026"
      ],
      "sources": [
        "source.nts.eitc.intro",
        "source.nts.grant.eligibility",
        "source.nts.grant.deadline",
        "source.nts.grant.2026-regular-press"
      ],
      "law_reference": "",
      "tags": [
        "cash-support"
      ],
      "criteria": [
        {
          "label": "단독가구 총소득",
          "basis": "부부합산 총소득",
          "condition": "2,200만원 미만",
          "threshold_krw_max": 22000000,
          "max_amount_krw": 1650000,
          "source": "source.nts.eitc.intro"
        },
        {
          "label": "홑벌이가구 총소득",
          "basis": "부부합산 총소득",
          "condition": "3,200만원 미만",
          "threshold_krw_max": 32000000,
          "max_amount_krw": 2850000,
          "source": "source.nts.eitc.intro"
        },
        {
          "label": "맞벌이가구 총소득",
          "basis": "부부합산 총소득",
          "condition": "4,400만원 미만",
          "threshold_krw_max": 44000000,
          "max_amount_krw": 3300000,
          "source": "source.nts.eitc.intro"
        },
        {
          "label": "재산요건",
          "basis": "가구원 전체 재산 합계액",
          "condition": "2억4천만원 미만",
          "threshold_krw_max": 240000000,
          "benefit": "신청 가능",
          "source": "source.nts.grant.2026-regular-press"
        },
        {
          "label": "재산 감액구간",
          "basis": "가구원 전체 재산 합계액",
          "condition": "1억7천만원 이상 2억4천만원 미만",
          "threshold_krw_min": 170000000,
          "threshold_krw_max": 240000000,
          "benefit": "산정액의 50% 지급",
          "source": "source.nts.grant.2026-regular-press"
        }
      ]
    },
    {
      "id": "support.hessal-119",
      "title": "햇살론119",
      "type": "support-program",
      "description": "은행권 채무조정 프로그램을 성실상환 중인 연 매출 3억원 이하 영세 개인사업자에게 사업 운영 신규 운전자금을 보증부 대출로 지원하는 상품입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "category.business-tax-compliance",
        "support.long-term-delinquent-debt-adjustment"
      ],
      "terms": [
        "term.policy-finance",
        "term.policy-loan",
        "term.debt-adjustment",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.kinfa.hessal-119"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "loan",
        "small-business"
      ],
      "criteria": [
        {
          "label": "채무조정 이용기간",
          "basis": "은행권 채무조정 프로그램",
          "condition": "3개월 이상 이용 중",
          "source": "source.kinfa.hessal-119",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "성실상환",
          "basis": "상환상태",
          "condition": "신청일 현재 연체 중이 아님",
          "source": "source.kinfa.hessal-119",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "연매출",
          "basis": "개인사업자 연 매출",
          "condition": "3억원 이하",
          "threshold_krw_max": 300000000,
          "source": "source.kinfa.hessal-119"
        },
        {
          "label": "대출한도",
          "basis": "신규·추가 운전자금",
          "condition": "최대 2,000만원",
          "limit_krw": 20000000,
          "note": "신규 1,000만원 + 추가 1,000만원",
          "source": "source.kinfa.hessal-119"
        },
        {
          "label": "대출금리",
          "basis": "은행별 대출금리",
          "condition": "연 6~7% 수준",
          "rate_percent_min": 6,
          "rate_percent_max": 7,
          "rate_label": "금리",
          "source": "source.kinfa.hessal-119",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        },
        {
          "label": "보증료",
          "basis": "보증료율",
          "condition": "연 0.5%",
          "rate_percent": 0.5,
          "rate_label": "보증료율",
          "source": "source.kinfa.hessal-119",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        }
      ]
    },
    {
      "id": "support.hessal-loan-youth",
      "title": "햇살론유스",
      "type": "support-program",
      "description": "대학생, 미취업청년, 사회초년생, 저소득 청년 개인사업자의 학업·취업준비·사회진입 자금을 보증 지원하는 서민금융진흥원 정책대출입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.youth-future-savings",
        "support.youth-leap-account"
      ],
      "terms": [
        "term.policy-finance",
        "term.policy-loan",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.kinfa.hessal-loan-youth"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "loan",
        "youth"
      ],
      "criteria": [
        {
          "label": "연령·소득",
          "basis": "만 나이와 연소득",
          "condition": "19세 이상 34세 이하이면서 연소득 3,500만원 이하",
          "threshold_krw_max": 35000000,
          "source": "source.kinfa.hessal-loan-youth"
        },
        {
          "label": "취업준비생",
          "basis": "지원대상",
          "condition": "대학(원)생, 학점은행제 수강자, 미취업청년",
          "source": "source.kinfa.hessal-loan-youth",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "사회초년생",
          "basis": "지원대상",
          "condition": "중소기업에 1년 이하 재직 중",
          "source": "source.kinfa.hessal-loan-youth",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "청년사업자",
          "basis": "지원대상",
          "condition": "창업 1년 이하 저소득 청년 개인사업자",
          "source": "source.kinfa.hessal-loan-youth",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "동일인 한도",
          "basis": "보증한도",
          "condition": "1인 최대 1,200만원",
          "limit_krw": 12000000,
          "note": "상환 후에도 한도 재부여 없음",
          "source": "source.kinfa.hessal-loan-youth"
        },
        {
          "label": "일반생활자금 연간한도",
          "basis": "보증한도",
          "condition": "연간 600만원",
          "limit_krw": 6000000,
          "source": "source.kinfa.hessal-loan-youth"
        },
        {
          "label": "특정용도자금 연간한도",
          "basis": "보증한도",
          "condition": "연간 900만원",
          "limit_krw": 9000000,
          "source": "source.kinfa.hessal-loan-youth"
        }
      ]
    },
    {
      "id": "support.illegal-private-finance-prevention-loan",
      "title": "불법사금융예방대출",
      "type": "support-program",
      "description": "대부업조차 이용이 어려운 저신용·저소득자의 생계비를 지원해 불법사금융 피해를 예방하는 서민금융진흥원 정책서민금융상품입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.basic-livelihood-benefit"
      ],
      "terms": [
        "term.policy-finance",
        "term.policy-loan",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.kinfa.illegal-private-finance-prevention-loan"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "loan",
        "vulnerable-finance"
      ],
      "criteria": [
        {
          "label": "신용요건",
          "basis": "개인신용평점",
          "condition": "하위 20%",
          "benefit": "신청 대상",
          "source": "source.kinfa.illegal-private-finance-prevention-loan",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "소득요건",
          "basis": "연소득",
          "condition": "3,500만원 이하",
          "threshold_krw_max": 35000000,
          "source": "source.kinfa.illegal-private-finance-prevention-loan"
        },
        {
          "label": "필수 이수·가입",
          "basis": "사전요건",
          "condition": "금융교육 이수 또는 복지멤버십 가입",
          "source": "source.kinfa.illegal-private-finance-prevention-loan",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "대출한도",
          "basis": "1인당 한도",
          "condition": "최대 100만원",
          "limit_krw": 1000000,
          "note": "연체자는 기본 50만원+추가 50만원, 특정용도 증빙 시 기본 최대 100만원",
          "source": "source.kinfa.illegal-private-finance-prevention-loan"
        },
        {
          "label": "일반 금리",
          "basis": "대출금리",
          "condition": "일반",
          "rate_percent": 12.5,
          "rate_label": "금리",
          "source": "source.kinfa.illegal-private-finance-prevention-loan",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        },
        {
          "label": "사회적배려대상자 금리",
          "basis": "대출금리",
          "condition": "사회적배려대상자",
          "rate_percent": 9.9,
          "rate_label": "금리",
          "source": "source.kinfa.illegal-private-finance-prevention-loan",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        },
        {
          "label": "완제자 재대출 금리",
          "basis": "대출금리",
          "condition": "6개월 이상 이용 후 완제자 재대출",
          "rate_percent": 4.5,
          "rate_label": "금리",
          "source": "source.kinfa.illegal-private-finance-prevention-loan",
          "amount_applicability": "비율 기준이며 고정 원화 금액 없음"
        }
      ]
    },
    {
      "id": "support.isa",
      "title": "개인종합자산관리계좌 ISA",
      "type": "support-program",
      "description": "개인이 예·적금, 펀드, 파생결합증권 등을 한 계좌에서 운용하며 세제혜택을 받을 수 있는 정책성 금융계좌입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "tax.income"
      ],
      "terms": [
        "term.tax-credit"
      ],
      "deadlines": [],
      "sources": [
        "source.fsc.isa.policy",
        "source.moef.isa.tax-benefit"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "tax-preferred-account"
      ],
      "criteria": [
        {
          "label": "연 납입한도",
          "basis": "ISA 납입금",
          "condition": "연간 납입한도",
          "limit_krw": 20000000,
          "source": "source.fsc.isa.policy"
        },
        {
          "label": "총 납입한도",
          "basis": "ISA 납입금",
          "condition": "5년 누적 한도",
          "limit_krw": 100000000,
          "source": "source.fsc.isa.policy"
        },
        {
          "label": "일반형 비과세",
          "basis": "계좌 순소득",
          "condition": "일반형 ISA",
          "limit_krw": 2000000,
          "benefit": "한도 내 비과세",
          "source": "source.moef.isa.tax-benefit"
        },
        {
          "label": "서민·농어민형 비과세",
          "basis": "계좌 순소득",
          "condition": "서민·농어민형 ISA",
          "limit_krw": 4000000,
          "benefit": "한도 내 비과세",
          "source": "source.moef.isa.tax-benefit"
        },
        {
          "label": "비과세 초과분 분리과세",
          "basis": "비과세 한도 초과 순소득",
          "condition": "비과세 한도 초과분",
          "rate_percent": 9,
          "rate_label": "분리과세율",
          "amount_formula": "비과세 한도 초과 순소득 × 9%",
          "source": "source.moef.isa.tax-benefit"
        }
      ]
    },
    {
      "id": "support.long-term-delinquent-debt-adjustment",
      "title": "장기연체자 특별채무조정",
      "type": "support-program",
      "description": "새도약기금 관련 장기연체채권 중 상환능력이 있는 채무자를 대상으로 신용회복위원회가 이자 감면, 원금감면, 분할상환, 상환유예를 지원하는 채무조정 제도입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.hessal-119"
      ],
      "terms": [
        "term.debt-adjustment",
        "term.median-income",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.ccrs.long-term-delinquent-debt-adjustment"
      ],
      "law_reference": "",
      "tags": [
        "debt-adjustment",
        "policy-finance",
        "vulnerable-finance"
      ],
      "criteria": [
        {
          "label": "연체기간",
          "basis": "채무조정 신청일 기준 연체채무",
          "condition": "5년 이상",
          "source": "source.ccrs.long-term-delinquent-debt-adjustment",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "1인 가구 소득",
          "basis": "2026년 기준중위소득 125%",
          "condition": "3,205,298원 이하",
          "threshold_krw_max": 3205298,
          "source": "source.ccrs.long-term-delinquent-debt-adjustment"
        },
        {
          "label": "2인 가구 소득",
          "basis": "2026년 기준중위소득 125%",
          "condition": "5,249,115원 이하",
          "threshold_krw_max": 5249115,
          "source": "source.ccrs.long-term-delinquent-debt-adjustment"
        },
        {
          "label": "3인 가구 소득",
          "basis": "2026년 기준중위소득 125%",
          "condition": "6,698,795원 이하",
          "threshold_krw_max": 6698795,
          "source": "source.ccrs.long-term-delinquent-debt-adjustment"
        },
        {
          "label": "4인 가구 소득",
          "basis": "2026년 기준중위소득 125%",
          "condition": "8,118,423원 이하",
          "threshold_krw_max": 8118423,
          "source": "source.ccrs.long-term-delinquent-debt-adjustment"
        },
        {
          "label": "채무감면",
          "basis": "연체이자·이자·원금",
          "condition": "연체이자 및 이자 전액 감면, 원금 최대 30~80% 감면",
          "rate_percent_min": 30,
          "rate_percent_max": 80,
          "rate_label": "감면율",
          "source": "source.ccrs.long-term-delinquent-debt-adjustment",
          "amount_formula": "연체이자·이자·원금 × 감면율 30%~80%"
        },
        {
          "label": "분할상환",
          "basis": "상환기간",
          "condition": "최장 10년 이내 원금균등분할상환",
          "source": "source.ccrs.long-term-delinquent-debt-adjustment",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "상환유예",
          "basis": "유예기간·유예이자율",
          "condition": "최장 3년 이내 유예, 유예이자율 연 2%",
          "rate_percent": 2,
          "rate_label": "유예이자율",
          "source": "source.ccrs.long-term-delinquent-debt-adjustment",
          "amount_formula": "유예기간·유예이자율 × 유예이자율 2%"
        }
      ]
    },
    {
      "id": "support.youth-future-savings",
      "title": "청년미래적금",
      "type": "support-program",
      "description": "2026년 6월 출시 예정인 청년 자산형성 정책형 적금입니다. 월 납입액에 대해 일반형과 우대형 정부기여금을 매칭하고 이자소득 비과세 특례를 연결합니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.youth-leap-account",
        "tax.income",
        "support.hessal-loan-youth"
      ],
      "terms": [
        "term.policy-finance",
        "term.median-income",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.fsc.youth-future-savings"
      ],
      "law_reference": "",
      "tags": [
        "asset-building",
        "policy-finance",
        "planned-2026"
      ],
      "criteria": [
        {
          "label": "출시 예정",
          "basis": "상품 출시",
          "condition": "2026년 6월 출시 예정",
          "benefit": "청년 자산형성 적금",
          "source": "source.fsc.youth-future-savings",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "가입연령",
          "basis": "만 나이",
          "condition": "19세 이상 34세 이하",
          "note": "청년기본법상 청년 기준",
          "source": "source.fsc.youth-future-savings",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "일반형 개인소득",
          "basis": "개인소득",
          "condition": "6,000만원 이하",
          "threshold_krw_max": 60000000,
          "source": "source.fsc.youth-future-savings"
        },
        {
          "label": "일반형 소상공인 매출",
          "basis": "연매출",
          "condition": "3억원 이하 소상공인",
          "threshold_krw_max": 300000000,
          "source": "source.fsc.youth-future-savings"
        },
        {
          "label": "일반형 가구소득",
          "basis": "기준 중위소득",
          "condition": "200% 이하",
          "benefit": "일반형 가입 가능",
          "source": "source.fsc.youth-future-savings",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "우대형 개인소득",
          "basis": "개인소득",
          "condition": "3,600만원 이하 중소기업 재직자",
          "threshold_krw_max": 36000000,
          "source": "source.fsc.youth-future-savings"
        },
        {
          "label": "우대형 소상공인 매출",
          "basis": "연매출",
          "condition": "1억원 이하 소상공인",
          "threshold_krw_max": 100000000,
          "source": "source.fsc.youth-future-savings"
        },
        {
          "label": "우대형 가구소득",
          "basis": "기준 중위소득",
          "condition": "150% 이하",
          "benefit": "우대형 가입 가능",
          "source": "source.fsc.youth-future-savings",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "월 납입한도",
          "basis": "월 납입금",
          "condition": "최대 50만원 자유적립",
          "limit_krw": 500000,
          "source": "source.fsc.youth-future-savings"
        },
        {
          "label": "일반형 기여금",
          "basis": "월 납입금",
          "condition": "일반형",
          "rate_percent": 6,
          "rate_label": "기여금비율",
          "benefit": "정부기여금 매칭",
          "source": "source.fsc.youth-future-savings",
          "amount_formula": "월 납입금 × 기여금비율 6%"
        },
        {
          "label": "우대형 기여금",
          "basis": "월 납입금",
          "condition": "우대형",
          "rate_percent": 12,
          "rate_label": "기여금비율",
          "benefit": "정부기여금 매칭",
          "source": "source.fsc.youth-future-savings",
          "amount_formula": "월 납입금 × 기여금비율 12%"
        },
        {
          "label": "만기",
          "basis": "가입기간",
          "condition": "3년",
          "benefit": "이자소득 비과세 특례 예정",
          "source": "source.fsc.youth-future-savings",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "support.youth-leap-account",
      "title": "청년도약계좌",
      "type": "support-program",
      "description": "청년의 중장기 자산형성을 지원하는 정책금융 상품입니다. 세금 세목은 아니지만 소득 요건, 금융소득종합과세 이력 제한, 비과세·정부기여금 학습 항목으로 연결합니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "tax.income",
        "support.youth-future-savings",
        "support.hessal-loan-youth"
      ],
      "terms": [
        "term.total-income",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.kinfa.youth-leap"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance"
      ],
      "criteria": [
        {
          "label": "나이",
          "basis": "계좌개설일 기준 만 나이",
          "condition": "19세 이상 34세 이하",
          "note": "병역이행기간은 최대 6년까지 차감",
          "source": "source.kinfa.youth-leap",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "개인소득 총급여",
          "basis": "직전 과세기간 총급여액",
          "condition": "7,500만원 이하",
          "threshold_krw_max": 75000000,
          "source": "source.kinfa.youth-leap"
        },
        {
          "label": "개인소득 종합소득",
          "basis": "종합소득과세표준에 합산되는 종합소득금액",
          "condition": "6,300만원 이하",
          "threshold_krw_max": 63000000,
          "source": "source.kinfa.youth-leap"
        },
        {
          "label": "가구소득",
          "basis": "가구원 수별 기준 중위소득",
          "condition": "250% 이하",
          "benefit": "가입 대상",
          "source": "source.kinfa.youth-leap",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "금융소득종합과세 제외",
          "basis": "직전 3개 과세기간",
          "condition": "금융소득종합과세 대상 이력 없음",
          "benefit": "가입 가능",
          "source": "source.kinfa.youth-leap",
          "amount_applicability": "정액 금액 기준 없음"
        }
      ]
    },
    {
      "id": "support.youth-special-rent-guarantee",
      "title": "무주택 청년 특례전세자금보증",
      "type": "support-program",
      "description": "무주택 청년 등 주거취약 대상에게 일반전세자금보증보다 완화된 요건과 보증한도를 적용하는 한국주택금융공사 특례보증입니다.",
      "folder": "30_Supports",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.policy-supports"
      ],
      "children": [],
      "related": [
        "support.didimdol-loan",
        "credit.monthly-rent"
      ],
      "terms": [
        "term.policy-finance",
        "term.policy-loan",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.hf.special-rent-guarantee"
      ],
      "law_reference": "",
      "tags": [
        "policy-finance",
        "housing",
        "guarantee",
        "youth"
      ],
      "criteria": [
        {
          "label": "무주택 청년 연령",
          "basis": "신청일 기준 만 나이",
          "condition": "만 34세 이하",
          "source": "source.hf.special-rent-guarantee",
          "amount_applicability": "정액 금액 기준 없음"
        },
        {
          "label": "무주택 청년 소득",
          "basis": "본인과 배우자 합산 연소득",
          "condition": "7,000만원 이하",
          "threshold_krw_max": 70000000,
          "source": "source.hf.special-rent-guarantee"
        },
        {
          "label": "무주택 청년 보증한도",
          "basis": "보증한도",
          "condition": "최대 2억원",
          "limit_krw": 200000000,
          "note": "1억원 이하 이용 시 상환능력별 보증한도 생략, 보증비율 100%",
          "source": "source.hf.special-rent-guarantee"
        },
        {
          "label": "다자녀가구 보증한도",
          "basis": "보증한도",
          "condition": "미성년 자녀 2명 이상",
          "limit_krw": 200000000,
          "source": "source.hf.special-rent-guarantee"
        }
      ]
    },
    {
      "id": "tax.comprehensive-real-estate",
      "title": "종합부동산세",
      "type": "tax",
      "description": "일정 기준을 넘는 주택·토지 보유에 대해 과세되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [
        "concept.cre-tax-base-date",
        "concept.cre-deduction-thresholds"
      ],
      "related": [
        "local.property",
        "support.didimdol-loan"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-law",
        "term.publicly-notified-price",
        "term.tax-rate",
        "term.eligibility-threshold"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.comprehensive-real-estate.overview",
        "source.nts.comprehensive-real-estate.rates",
        "source.nts.real-estate-tax.faq"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "주택 공제금액",
          "basis": "공시가격 합계액",
          "condition": "주택",
          "deduction_krw": 900000000,
          "note": "1세대 1주택자는 12억원",
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "1세대 1주택자 주택 공제금액",
          "basis": "공시가격 합계액",
          "condition": "1세대 1주택자",
          "deduction_krw": 1200000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "종합합산토지 공제금액",
          "basis": "공시가격 합계액",
          "condition": "종합합산토지",
          "deduction_krw": 500000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "별도합산토지 공제금액",
          "basis": "공시가격 합계액",
          "condition": "별도합산토지",
          "deduction_krw": 8000000000,
          "source": "source.nts.comprehensive-real-estate.overview"
        },
        {
          "label": "주택 2주택 이하 3억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 3억원 이하",
          "threshold_krw_max": 300000000,
          "rate_percent": 0.5,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 6억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 6억원 이하",
          "threshold_krw_max": 600000000,
          "rate_percent": 0.7,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 12억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 12억원 이하",
          "threshold_krw_max": 1200000000,
          "rate_percent": 1.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 25억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 25억원 이하",
          "threshold_krw_max": 2500000000,
          "rate_percent": 1.3,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 50억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 50억원 이하",
          "threshold_krw_max": 5000000000,
          "rate_percent": 1.5,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 94억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 94억원 이하",
          "threshold_krw_max": 9400000000,
          "rate_percent": 2.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 2주택 이하 94억원 초과",
          "basis": "종부세 과세표준",
          "condition": "주택 2주택 이하, 94억원 초과",
          "threshold_krw_min": 9400000000,
          "rate_percent": 2.7,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 3주택 이상 25억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 3주택 이상, 25억원 이하",
          "threshold_krw_max": 2500000000,
          "rate_percent": 2.0,
          "note": "3억원 이하 0.5%, 6억원 이하 0.7%, 12억원 이하 1.0%",
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 3주택 이상 50억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 3주택 이상, 50억원 이하",
          "threshold_krw_max": 5000000000,
          "rate_percent": 3.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 3주택 이상 94억원 이하",
          "basis": "종부세 과세표준",
          "condition": "주택 3주택 이상, 94억원 이하",
          "threshold_krw_max": 9400000000,
          "rate_percent": 4.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "주택 3주택 이상 94억원 초과",
          "basis": "종부세 과세표준",
          "condition": "주택 3주택 이상, 94억원 초과",
          "threshold_krw_min": 9400000000,
          "rate_percent": 5.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "종합합산토지 15억원 이하",
          "basis": "종부세 과세표준",
          "condition": "종합합산토지 15억원 이하",
          "threshold_krw_max": 1500000000,
          "rate_percent": 1.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "종합합산토지 45억원 이하",
          "basis": "종부세 과세표준",
          "condition": "종합합산토지 45억원 이하",
          "threshold_krw_max": 4500000000,
          "rate_percent": 2.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "종합합산토지 45억원 초과",
          "basis": "종부세 과세표준",
          "condition": "종합합산토지 45억원 초과",
          "threshold_krw_min": 4500000000,
          "rate_percent": 3.0,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "별도합산토지 200억원 이하",
          "basis": "종부세 과세표준",
          "condition": "별도합산토지 200억원 이하",
          "threshold_krw_max": 20000000000,
          "rate_percent": 0.5,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "별도합산토지 400억원 이하",
          "basis": "종부세 과세표준",
          "condition": "별도합산토지 400억원 이하",
          "threshold_krw_max": 40000000000,
          "rate_percent": 0.6,
          "source": "source.nts.comprehensive-real-estate.rates"
        },
        {
          "label": "별도합산토지 400억원 초과",
          "basis": "종부세 과세표준",
          "condition": "별도합산토지 400억원 초과",
          "threshold_krw_min": 40000000000,
          "rate_percent": 0.7,
          "source": "source.nts.comprehensive-real-estate.rates"
        }
      ]
    },
    {
      "id": "tax.corporate",
      "title": "법인세",
      "type": "tax",
      "description": "법인의 각 사업연도 소득 등에 과세되는 국세이며 법인세 공제·감면 지원제도와 직접 연결됩니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [
        "category.corporate-tax-supports",
        "local.local-income"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-law",
        "term.tax-base",
        "term.tax-rate",
        "term.progressive-deduction"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.corporate-tax.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "2억원 이하",
          "basis": "각 사업연도 소득 과세표준",
          "condition": "2억원 이하",
          "threshold_krw_max": 200000000,
          "rate_percent": 10,
          "progressive_deduction_krw": 0,
          "note": "2026.1.1. 이후 개시 사업연도 기준",
          "source": "source.nts.corporate-tax.rates"
        },
        {
          "label": "2억원 초과 200억원 이하",
          "basis": "각 사업연도 소득 과세표준",
          "condition": "2억원 초과 200억원 이하",
          "threshold_krw_min": 200000000,
          "threshold_krw_max": 20000000000,
          "rate_percent": 20,
          "progressive_deduction_krw": 20000000,
          "note": "2026.1.1. 이후 개시 사업연도 기준",
          "source": "source.nts.corporate-tax.rates"
        },
        {
          "label": "200억원 초과 3,000억원 이하",
          "basis": "각 사업연도 소득 과세표준",
          "condition": "200억원 초과 3,000억원 이하",
          "threshold_krw_min": 20000000000,
          "threshold_krw_max": 300000000000,
          "rate_percent": 22,
          "progressive_deduction_krw": 420000000,
          "note": "2026.1.1. 이후 개시 사업연도 기준",
          "source": "source.nts.corporate-tax.rates"
        },
        {
          "label": "3,000억원 초과",
          "basis": "각 사업연도 소득 과세표준",
          "condition": "3,000억원 초과",
          "threshold_krw_min": 300000000000,
          "rate_percent": 25,
          "progressive_deduction_krw": 9420000000,
          "note": "2026.1.1. 이후 개시 사업연도 기준",
          "source": "source.nts.corporate-tax.rates"
        }
      ]
    },
    {
      "id": "tax.customs",
      "title": "관세",
      "type": "tax",
      "description": "수입물품에 부과되는 조세입니다. 국세기본법 제2조의 국세 열거와 별도로 관세법 제14조를 근거로 관리합니다.",
      "folder": "10_Taxes/Customs",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "category.customs"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.customs",
        "term.tax-base"
      ],
      "deadlines": [],
      "sources": [
        "source.customs-act.2026.article14",
        "source.law.customs-tariff"
      ],
      "law_reference": "관세법 제14조",
      "tags": [],
      "criteria": [
        {
          "label": "수입물품 관세",
          "basis": "수입물품 과세가격",
          "condition": "품목분류별 관세율표 적용",
          "amount_formula": "과세가격 × 품목별 관세율",
          "source": "source.law.customs-tariff"
        }
      ]
    },
    {
      "id": "tax.education",
      "title": "교육세",
      "type": "tax",
      "description": "교육재정 확충을 위한 목적세 성격의 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [
        "local.local-education"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.education-tax-act.article5"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "교육세 부가 과세",
          "basis": "개별소비세액·교통세액·금융보험업 수익금액 등",
          "condition": "교육세법상 납세의무자",
          "amount_formula": "교육세 과세표준 × 교육세법상 세율",
          "source": "source.law.education-tax-act.article5"
        }
      ]
    },
    {
      "id": "tax.gift",
      "title": "증여세",
      "type": "tax",
      "description": "무상 이전되는 재산에 과세되는 세금입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.inheritance-and-gift"
      ],
      "children": [
        "filing.gift-tax-return"
      ],
      "related": [],
      "terms": [
        "term.tax-base",
        "term.donee",
        "term.tax-rate",
        "term.progressive-deduction"
      ],
      "deadlines": [
        "deadline.gift.general"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.gift.deadline",
        "source.nts.gift.rates"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "1억원 이하",
          "basis": "과세표준",
          "condition": "1억원 이하",
          "threshold_krw_max": 100000000,
          "rate_percent": 10,
          "progressive_deduction_krw": 0,
          "source": "source.nts.gift.rates"
        },
        {
          "label": "1억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "1억원 초과 5억원 이하",
          "threshold_krw_min": 100000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 20,
          "progressive_deduction_krw": 10000000,
          "source": "source.nts.gift.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 30,
          "progressive_deduction_krw": 60000000,
          "source": "source.nts.gift.rates"
        },
        {
          "label": "10억원 초과 30억원 이하",
          "basis": "과세표준",
          "condition": "10억원 초과 30억원 이하",
          "threshold_krw_min": 1000000000,
          "threshold_krw_max": 3000000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 160000000,
          "source": "source.nts.gift.rates"
        },
        {
          "label": "30억원 초과",
          "basis": "과세표준",
          "condition": "30억원 초과",
          "threshold_krw_min": 3000000000,
          "rate_percent": 50,
          "progressive_deduction_krw": 460000000,
          "source": "source.nts.gift.rates"
        }
      ]
    },
    {
      "id": "tax.income",
      "title": "소득세",
      "type": "tax",
      "description": "개인의 소득에 과세되는 국세입니다. 종합소득, 퇴직소득, 양도소득 흐름으로 세부 학습 노드를 둡니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [
        "tax.income.comprehensive",
        "tax.income.retirement",
        "tax.income.capital-gains"
      ],
      "related": [
        "category.income-deductions",
        "category.tax-credits",
        "local.local-income",
        "support.youth-future-savings",
        "support.youth-leap-account",
        "support.isa"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-law",
        "term.tax-base",
        "term.tax-rate",
        "term.progressive-deduction"
      ],
      "deadlines": [
        "deadline.income-tax.2025-return",
        "deadline.year-end-settlement"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.income-tax.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "1,400만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 이하",
          "threshold_krw_max": 14000000,
          "rate_percent": 6,
          "progressive_deduction_krw": 0,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1,400만원 초과 5,000만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 초과 5,000만원 이하",
          "threshold_krw_min": 14000000,
          "threshold_krw_max": 50000000,
          "rate_percent": 15,
          "progressive_deduction_krw": 1260000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5,000만원 초과 8,800만원 이하",
          "basis": "과세표준",
          "condition": "5,000만원 초과 8,800만원 이하",
          "threshold_krw_min": 50000000,
          "threshold_krw_max": 88000000,
          "rate_percent": 24,
          "progressive_deduction_krw": 5760000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "8,800만원 초과 1억5,000만원 이하",
          "basis": "과세표준",
          "condition": "8,800만원 초과 1억5,000만원 이하",
          "threshold_krw_min": 88000000,
          "threshold_krw_max": 150000000,
          "rate_percent": 35,
          "progressive_deduction_krw": 15440000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1억5,000만원 초과 3억원 이하",
          "basis": "과세표준",
          "condition": "1억5,000만원 초과 3억원 이하",
          "threshold_krw_min": 150000000,
          "threshold_krw_max": 300000000,
          "rate_percent": 38,
          "progressive_deduction_krw": 19940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "3억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "3억원 초과 5억원 이하",
          "threshold_krw_min": 300000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 25940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 42,
          "progressive_deduction_krw": 35940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "10억원 초과",
          "basis": "과세표준",
          "condition": "10억원 초과",
          "threshold_krw_min": 1000000000,
          "rate_percent": 45,
          "progressive_deduction_krw": 65940000,
          "source": "source.nts.income-tax.rates"
        }
      ]
    },
    {
      "id": "tax.income.capital-gains",
      "title": "양도소득세",
      "type": "tax",
      "description": "부동산, 주식 등 자산 양도차익에 대해 과세되는 소득세입니다. 자산 유형별 특례세율이 있으므로 기본세율과 특례세율을 분리해 확인합니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.income"
      ],
      "children": [
        "concept.capital-gains.calculation-flow",
        "concept.capital-gains.stock-basic-deduction",
        "filing.capital-gains-return"
      ],
      "related": [
        "tax.securities-transaction"
      ],
      "terms": [
        "term.tax-base",
        "term.capital-gain",
        "term.tax-rate",
        "term.deadline"
      ],
      "deadlines": [
        "deadline.capital-gains.preliminary",
        "deadline.capital-gains.final"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.capital-gains.overview",
        "source.nts.capital-gains.deadline",
        "source.nts.capital-gains.rates"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "1,400만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 이하",
          "threshold_krw_max": 14000000,
          "rate_percent": 6,
          "progressive_deduction_krw": 0,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1,400만원 초과 5,000만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 초과 5,000만원 이하",
          "threshold_krw_min": 14000000,
          "threshold_krw_max": 50000000,
          "rate_percent": 15,
          "progressive_deduction_krw": 1260000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5,000만원 초과 8,800만원 이하",
          "basis": "과세표준",
          "condition": "5,000만원 초과 8,800만원 이하",
          "threshold_krw_min": 50000000,
          "threshold_krw_max": 88000000,
          "rate_percent": 24,
          "progressive_deduction_krw": 5760000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "8,800만원 초과 1억5,000만원 이하",
          "basis": "과세표준",
          "condition": "8,800만원 초과 1억5,000만원 이하",
          "threshold_krw_min": 88000000,
          "threshold_krw_max": 150000000,
          "rate_percent": 35,
          "progressive_deduction_krw": 15440000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1억5,000만원 초과 3억원 이하",
          "basis": "과세표준",
          "condition": "1억5,000만원 초과 3억원 이하",
          "threshold_krw_min": 150000000,
          "threshold_krw_max": 300000000,
          "rate_percent": 38,
          "progressive_deduction_krw": 19940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "3억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "3억원 초과 5억원 이하",
          "threshold_krw_min": 300000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 25940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 42,
          "progressive_deduction_krw": 35940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "10억원 초과",
          "basis": "과세표준",
          "condition": "10억원 초과",
          "threshold_krw_min": 1000000000,
          "rate_percent": 45,
          "progressive_deduction_krw": 65940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "국외 중소기업주식 등",
          "basis": "양도소득 과세표준",
          "condition": "국외 중소기업주식 등",
          "rate_percent": 10,
          "source": "source.nts.capital-gains.rates",
          "amount_formula": "양도소득 과세표준 × 적용비율 10%"
        },
        {
          "label": "국외 그 밖의 주식 등",
          "basis": "양도소득 과세표준",
          "condition": "국외 그 밖의 주식 등",
          "rate_percent": 20,
          "source": "source.nts.capital-gains.rates",
          "amount_formula": "양도소득 과세표준 × 적용비율 20%"
        },
        {
          "label": "파생상품 등",
          "basis": "양도소득 과세표준",
          "condition": "2018.4.1. 이후 양도분",
          "rate_percent": 10,
          "note": "기본세율 20%에 한시적 탄력세율 적용",
          "source": "source.nts.capital-gains.rates",
          "amount_formula": "양도소득 과세표준 × 적용비율 10%"
        }
      ]
    },
    {
      "id": "tax.income.comprehensive",
      "title": "종합소득세",
      "type": "tax",
      "description": "이자·배당·사업·근로·연금·기타소득 등 종합소득금액에 대해 확정신고하는 소득세 흐름입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2025,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.income"
      ],
      "children": [],
      "related": [
        "support.earned-income-tax-credit",
        "filing.income-tax-return",
        "filing.business-income-withholding"
      ],
      "terms": [
        "term.tax-base",
        "term.tax-rate",
        "term.progressive-deduction",
        "term.deadline-special-rule"
      ],
      "deadlines": [
        "deadline.income-tax.2025-return"
      ],
      "sources": [
        "source.nts.income-tax.deadline",
        "source.nts.income-tax.rates"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "1,400만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 이하",
          "threshold_krw_max": 14000000,
          "rate_percent": 6,
          "progressive_deduction_krw": 0,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1,400만원 초과 5,000만원 이하",
          "basis": "과세표준",
          "condition": "1,400만원 초과 5,000만원 이하",
          "threshold_krw_min": 14000000,
          "threshold_krw_max": 50000000,
          "rate_percent": 15,
          "progressive_deduction_krw": 1260000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5,000만원 초과 8,800만원 이하",
          "basis": "과세표준",
          "condition": "5,000만원 초과 8,800만원 이하",
          "threshold_krw_min": 50000000,
          "threshold_krw_max": 88000000,
          "rate_percent": 24,
          "progressive_deduction_krw": 5760000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "8,800만원 초과 1억5,000만원 이하",
          "basis": "과세표준",
          "condition": "8,800만원 초과 1억5,000만원 이하",
          "threshold_krw_min": 88000000,
          "threshold_krw_max": 150000000,
          "rate_percent": 35,
          "progressive_deduction_krw": 15440000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "1억5,000만원 초과 3억원 이하",
          "basis": "과세표준",
          "condition": "1억5,000만원 초과 3억원 이하",
          "threshold_krw_min": 150000000,
          "threshold_krw_max": 300000000,
          "rate_percent": 38,
          "progressive_deduction_krw": 19940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "3억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "3억원 초과 5억원 이하",
          "threshold_krw_min": 300000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 25940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 42,
          "progressive_deduction_krw": 35940000,
          "source": "source.nts.income-tax.rates"
        },
        {
          "label": "10억원 초과",
          "basis": "과세표준",
          "condition": "10억원 초과",
          "threshold_krw_min": 1000000000,
          "rate_percent": 45,
          "progressive_deduction_krw": 65940000,
          "source": "source.nts.income-tax.rates"
        }
      ]
    },
    {
      "id": "tax.income.retirement",
      "title": "퇴직소득세",
      "type": "tax",
      "description": "퇴직으로 받는 소득에 대해 별도 계산 구조를 가지는 소득세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.income"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.withholding"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.retirement-income.calculation"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "퇴직소득세 계산 산식",
          "basis": "퇴직소득 과세표준",
          "condition": "2020년 이후 퇴직분",
          "amount_formula": "(과세표준 × 기본세율 - 누진공제액) ÷ 12 × 근속연수",
          "source": "source.nts.retirement-income.calculation"
        },
        {
          "label": "근속연수 5년 이하 공제",
          "basis": "근속연수공제",
          "condition": "5년 이하",
          "amount_formula": "근속연수 × 1,000,000원",
          "source": "source.nts.retirement-income.calculation"
        },
        {
          "label": "근속연수 10년 이하 공제",
          "basis": "근속연수공제",
          "condition": "5년 초과 10년 이하",
          "amount_formula": "5,000,000원 + (근속연수 - 5년) × 2,000,000원",
          "source": "source.nts.retirement-income.calculation"
        },
        {
          "label": "근속연수 20년 이하 공제",
          "basis": "근속연수공제",
          "condition": "10년 초과 20년 이하",
          "amount_formula": "15,000,000원 + (근속연수 - 10년) × 2,500,000원",
          "source": "source.nts.retirement-income.calculation"
        },
        {
          "label": "근속연수 20년 초과 공제",
          "basis": "근속연수공제",
          "condition": "20년 초과",
          "amount_formula": "40,000,000원 + (근속연수 - 20년) × 3,000,000원",
          "source": "source.nts.retirement-income.calculation"
        }
      ]
    },
    {
      "id": "tax.individual-consumption",
      "title": "개별소비세",
      "type": "tax",
      "description": "특정 물품, 장소, 행위 등에 개별적으로 부과되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.individual-consumption-tax-act.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "과세물품·장소별 세율",
          "basis": "과세가격 또는 과세수량",
          "condition": "개별소비세법상 과세물품·장소·행위",
          "amount_formula": "과세가격 × 품목별 세율 또는 과세수량 × 품목별 정액세",
          "source": "source.law.individual-consumption-tax-act.rates"
        }
      ]
    },
    {
      "id": "tax.inheritance",
      "title": "상속세",
      "type": "tax",
      "description": "사망으로 이전되는 재산에 과세되는 세금입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [
        "tax.inheritance-and-gift"
      ],
      "children": [
        "filing.inheritance-tax-return"
      ],
      "related": [],
      "terms": [
        "term.tax-base",
        "term.heir",
        "term.tax-rate",
        "term.progressive-deduction"
      ],
      "deadlines": [
        "deadline.inheritance.resident",
        "deadline.inheritance.nonresident"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.inheritance.overview",
        "source.nts.inheritance.rates"
      ],
      "law_reference": "",
      "tags": [],
      "criteria": [
        {
          "label": "1억원 이하",
          "basis": "과세표준",
          "condition": "1억원 이하",
          "threshold_krw_max": 100000000,
          "rate_percent": 10,
          "progressive_deduction_krw": 0,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "1억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "1억원 초과 5억원 이하",
          "threshold_krw_min": 100000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 20,
          "progressive_deduction_krw": 10000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 30,
          "progressive_deduction_krw": 60000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "10억원 초과 30억원 이하",
          "basis": "과세표준",
          "condition": "10억원 초과 30억원 이하",
          "threshold_krw_min": 1000000000,
          "threshold_krw_max": 3000000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 160000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "30억원 초과",
          "basis": "과세표준",
          "condition": "30억원 초과",
          "threshold_krw_min": 3000000000,
          "rate_percent": 50,
          "progressive_deduction_krw": 460000000,
          "source": "source.nts.inheritance.rates"
        }
      ]
    },
    {
      "id": "tax.inheritance-and-gift",
      "title": "상속세와 증여세",
      "type": "tax",
      "description": "상속 또는 증여로 이전되는 재산에 과세되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [
        "tax.inheritance",
        "tax.gift"
      ],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law",
        "term.heir",
        "term.donee",
        "term.tax-rate",
        "term.progressive-deduction"
      ],
      "deadlines": [
        "deadline.inheritance.resident",
        "deadline.gift.general"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.inheritance.overview",
        "source.nts.gift.deadline",
        "source.nts.inheritance.rates",
        "source.nts.gift.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "1억원 이하",
          "basis": "과세표준",
          "condition": "1억원 이하",
          "threshold_krw_max": 100000000,
          "rate_percent": 10,
          "progressive_deduction_krw": 0,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "1억원 초과 5억원 이하",
          "basis": "과세표준",
          "condition": "1억원 초과 5억원 이하",
          "threshold_krw_min": 100000000,
          "threshold_krw_max": 500000000,
          "rate_percent": 20,
          "progressive_deduction_krw": 10000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "5억원 초과 10억원 이하",
          "basis": "과세표준",
          "condition": "5억원 초과 10억원 이하",
          "threshold_krw_min": 500000000,
          "threshold_krw_max": 1000000000,
          "rate_percent": 30,
          "progressive_deduction_krw": 60000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "10억원 초과 30억원 이하",
          "basis": "과세표준",
          "condition": "10억원 초과 30억원 이하",
          "threshold_krw_min": 1000000000,
          "threshold_krw_max": 3000000000,
          "rate_percent": 40,
          "progressive_deduction_krw": 160000000,
          "source": "source.nts.inheritance.rates"
        },
        {
          "label": "30억원 초과",
          "basis": "과세표준",
          "condition": "30억원 초과",
          "threshold_krw_min": 3000000000,
          "rate_percent": 50,
          "progressive_deduction_krw": 460000000,
          "source": "source.nts.inheritance.rates"
        }
      ]
    },
    {
      "id": "tax.liquor",
      "title": "주세",
      "type": "tax",
      "description": "주류에 과세되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.liquor-tax-act.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "주류 종류별 세율",
          "basis": "주류 가격 또는 출고수량",
          "condition": "주정·탁주·맥주·증류주 등 주류 종류별",
          "amount_formula": "과세표준 × 종가세율 또는 출고수량 × 종량세율",
          "source": "source.law.liquor-tax-act.rates"
        }
      ]
    },
    {
      "id": "tax.securities-transaction",
      "title": "증권거래세",
      "type": "tax",
      "description": "주권 등의 양도 거래에 과세되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [
        "tax.income.capital-gains",
        "filing.capital-gains-return",
        "concept.capital-gains.stock-basic-deduction"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.securities-transaction-tax-act.article8"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "주권 양도 거래",
          "basis": "주권 등 양도가액",
          "condition": "주권 또는 지분 양도",
          "amount_formula": "양도가액 × 증권거래세법·시행령상 시장별 세율",
          "source": "source.law.securities-transaction-tax-act.article8"
        }
      ]
    },
    {
      "id": "tax.special-rural-development",
      "title": "농어촌특별세",
      "type": "tax",
      "description": "농어촌 경쟁력 강화 재원 등을 위해 부과되는 목적세 성격의 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.special-rural-development-tax-act.article5"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "농어촌특별세 부가 과세",
          "basis": "감면세액·증권거래금액·개별소비세액 등",
          "condition": "농어촌특별세법상 납세의무자",
          "amount_formula": "과세표준 × 농어촌특별세법상 세율",
          "source": "source.law.special-rural-development-tax-act.article5"
        }
      ]
    },
    {
      "id": "tax.stamp",
      "title": "인지세",
      "type": "tax",
      "description": "과세문서 작성에 대해 부과되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.stamp-tax-act.article3"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "1천만원 이하",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "1천만원 이하",
          "amount_krw": 0,
          "source": "source.law.stamp-tax-act.article3"
        },
        {
          "label": "1천만원 초과 3천만원 이하",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "1천만원 초과 3천만원 이하",
          "threshold_krw_min": 10000000,
          "threshold_krw_max": 30000000,
          "amount_krw": 20000,
          "source": "source.law.stamp-tax-act.article3"
        },
        {
          "label": "3천만원 초과 5천만원 이하",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "3천만원 초과 5천만원 이하",
          "threshold_krw_min": 30000000,
          "threshold_krw_max": 50000000,
          "amount_krw": 40000,
          "source": "source.law.stamp-tax-act.article3"
        },
        {
          "label": "5천만원 초과 1억원 이하",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "5천만원 초과 1억원 이하",
          "threshold_krw_min": 50000000,
          "threshold_krw_max": 100000000,
          "amount_krw": 70000,
          "source": "source.law.stamp-tax-act.article3"
        },
        {
          "label": "1억원 초과 10억원 이하",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "1억원 초과 10억원 이하",
          "threshold_krw_min": 100000000,
          "threshold_krw_max": 1000000000,
          "amount_krw": 150000,
          "source": "source.law.stamp-tax-act.article3"
        },
        {
          "label": "10억원 초과",
          "basis": "부동산 등 소유권 이전 과세문서 기재금액",
          "condition": "10억원 초과",
          "threshold_krw_min": 1000000000,
          "amount_krw": 350000,
          "source": "source.law.stamp-tax-act.article3"
        }
      ]
    },
    {
      "id": "tax.transport-energy-environment",
      "title": "교통·에너지·환경세",
      "type": "tax",
      "description": "교통시설, 에너지, 환경 관련 재원 목적의 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [],
      "related": [],
      "terms": [
        "term.national-tax",
        "term.tax-law"
      ],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.law.transport-energy-environment-tax-act.rates"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "유류 등 과세물품별 정액세",
          "basis": "과세물품 수량",
          "condition": "휘발유·경유 등 법정 과세물품",
          "amount_formula": "과세물품 수량 × 물품별 정액세율",
          "source": "source.law.transport-energy-environment-tax-act.rates"
        }
      ]
    },
    {
      "id": "tax.value-added",
      "title": "부가가치세",
      "type": "tax",
      "description": "재화 또는 용역의 공급 과정에서 생긴 부가가치에 과세되는 국세입니다.",
      "folder": "10_Taxes/National",
      "basis_year": 2026,
      "effective_date": "2026-01-01",
      "expiration_date": null,
      "parents": [
        "category.national-taxes"
      ],
      "children": [
        "concept.general-vat-taxpayer",
        "concept.simple-vat-taxpayer",
        "concept.vat-payment-exemption"
      ],
      "related": [
        "category.business-tax-compliance",
        "local.local-consumption",
        "filing.business-registration",
        "filing.vat-return"
      ],
      "terms": [
        "term.national-tax",
        "term.tax-period",
        "term.general-vat-taxpayer",
        "term.simple-vat-taxpayer",
        "term.tax-rate",
        "term.eligibility-threshold"
      ],
      "deadlines": [
        "deadline.vat.periodic",
        "deadline.vat.general.first-final",
        "deadline.vat.general.second-final",
        "deadline.vat.simplified.annual"
      ],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "국세기본법 제2조 제1호",
      "tags": [
        "national-tax"
      ],
      "criteria": [
        {
          "label": "일반과세자 매출 기준",
          "basis": "1년 매출액",
          "condition": "1억400만원 이상",
          "threshold_krw_min": 104000000,
          "benefit": "일반과세자",
          "source": "source.nts.vat.overview"
        },
        {
          "label": "간이과세자 매출 기준",
          "basis": "1년 매출액",
          "condition": "1억400만원 미만",
          "threshold_krw_max": 104000000,
          "benefit": "간이과세자",
          "source": "source.nts.vat.overview"
        },
        {
          "label": "일반과세자 세율",
          "basis": "매출세액",
          "condition": "매출액에 기본세율 적용",
          "rate_percent": 10,
          "note": "영세율 적용 대상은 0%",
          "source": "source.nts.vat.filing-duty",
          "amount_formula": "매출세액 × 적용비율 10%"
        },
        {
          "label": "간이과세자 업종별 부가가치율",
          "basis": "업종별 부가가치율",
          "condition": "2021.7.1. 이후 업종별 15%~40%",
          "rate_percent_min": 15,
          "rate_percent_max": 40,
          "note": "납부세액은 매출액 × 업종별 부가가치율 × 10% - 공제세액",
          "source": "source.nts.vat.overview",
          "amount_formula": "업종별 부가가치율 × 적용비율 15%~40%"
        },
        {
          "label": "간이과세자 예정신고 대상",
          "basis": "직전연도 공급대가",
          "condition": "4,800만원 이상 1억400만원 미만이고 예정부과기간에 세금계산서 발급",
          "threshold_krw_min": 48000000,
          "threshold_krw_max": 104000000,
          "source": "source.nts.vat.filing-duty"
        },
        {
          "label": "간이과세자 납부의무 면제",
          "basis": "직전연도 공급대가",
          "condition": "4,800만원 미만",
          "threshold_krw_max": 48000000,
          "benefit": "납부세액 납부의무 면제 가능",
          "source": "source.nts.vat.filing-duty"
        }
      ]
    },
    {
      "id": "term.capital-gain",
      "title": "양도차익",
      "type": "term",
      "description": "양도가액에서 취득가액과 필요경비 등을 차감해 산출하는 양도소득세 계산의 핵심 금액입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.capital-gains.overview"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.customs",
      "title": "관세",
      "type": "term",
      "description": "수입물품에 부과되는 조세입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.customs-act.2026.article14"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.deadline",
      "title": "법정신고기한",
      "type": "term",
      "description": "세법에 따라 과세표준신고서를 제출할 기한입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.deadline-special-rule",
      "title": "기한의 특례",
      "type": "term",
      "description": "신고·납부 기한일이 공휴일, 토요일 또는 근로자의 날이면 그 다음 날을 기한으로 보는 규칙입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.tax-calendar.2026",
        "source.nts.income-tax.deadline"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.debt-adjustment",
      "title": "채무조정",
      "type": "term",
      "description": "상환이 어려운 채무자의 이자율, 상환기간, 유예기간, 원금감면 등을 조정해 경제적 재기를 지원하는 제도입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.ccrs.long-term-delinquent-debt-adjustment"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.deduction-limit",
      "title": "소득공제 종합한도",
      "type": "term",
      "description": "과도한 소득공제 적용을 배제하기 위해 일정 소득공제 항목 합계에 적용되는 한도입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.donee",
      "title": "수증자",
      "type": "term",
      "description": "증여로 재산을 이전받아 증여세 신고·납부 의무자가 될 수 있는 사람입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.gift.deadline"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.eligibility-threshold",
      "title": "자격 기준금액",
      "type": "term",
      "description": "지원금, 공제, 과세유형 판정에서 대상 여부를 가르는 소득·매출·재산·주택가액 등의 기준금액입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.2026-regular-press",
        "source.nts.vat.overview"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.general-vat-taxpayer",
      "title": "일반과세자",
      "type": "term",
      "description": "부가가치세에서 일반 세율과 매입세액 공제 구조를 적용받는 과세사업자 유형입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.gross-pay",
      "title": "총급여액 등",
      "type": "term",
      "description": "장려금 지급액 결정과 홑벌이·맞벌이 구분 등에 쓰이는 근로, 사업, 종교인소득의 합계 기준입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.eligibility"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.heir",
      "title": "상속인",
      "type": "term",
      "description": "상속을 원인으로 재산을 물려받아 상속세 신고·납부 의무자가 될 수 있는 사람입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.inheritance.overview"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.income-deduction",
      "title": "소득공제",
      "type": "term",
      "description": "과세표준 계산 전에 소득금액에서 차감하는 공제입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.year-end-settlement.deduction-limit"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.local-tax",
      "title": "지방세",
      "type": "term",
      "description": "지방자치단체가 과세권을 가지며 지방세기본법상 세목과 자치단체 세목 배분에 따라 관리되는 세금입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.local-tax-framework-act.2026.article8"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.median-income",
      "title": "기준 중위소득",
      "type": "term",
      "description": "복지급여와 정책금융 지원대상 판정에 쓰이는 가구원 수별 중위소득 기준입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.govkr.basic-livelihood-benefit",
        "source.fsc.youth-future-savings"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.national-tax",
      "title": "국세",
      "type": "term",
      "description": "국가가 부과하는 조세 중 국세기본법 제2조가 열거한 세목입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.policy-finance",
      "title": "정책금융",
      "type": "term",
      "description": "정부, 금융위원회, 금융공공기관 등이 취약계층·청년·서민·실수요자의 금융 접근성과 자산형성을 지원하기 위해 운영하는 금융상품입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.fsc.youth-future-savings",
        "source.kinfa.illegal-private-finance-prevention-loan",
        "source.hf.didimdol-loan"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.policy-loan",
      "title": "정책대출",
      "type": "term",
      "description": "지원대상·한도·금리·보증요건을 정책적으로 정해 일반 금융 접근이 어려운 대상에게 제공하는 대출 또는 보증 상품입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.kinfa.hessal-loan-youth",
        "source.kinfa.hessal-119",
        "source.hf.didimdol-loan"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.progressive-deduction",
      "title": "누진공제",
      "type": "term",
      "description": "초과누진세율 구조에서 산출세액을 과세표준 × 세율 - 누진공제액 방식으로 계산할 때 차감하는 금액입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.income-tax.rates"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.property-requirement",
      "title": "재산요건",
      "type": "term",
      "description": "근로·자녀장려금에서 가구원 재산 합계액으로 판정하는 요건입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.eligibility"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.publicly-notified-price",
      "title": "공시가격",
      "type": "term",
      "description": "종합부동산세 등 부동산 보유세에서 과세대상 유형별 공제금액과 과세표준 계산에 쓰이는 공적 가격 기준입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.comprehensive-real-estate.overview"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.simple-vat-taxpayer",
      "title": "간이과세자",
      "type": "term",
      "description": "부가가치세에서 직전 1년 매출액이 10,400만원 미만인 개인사업자 유형입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.vat.overview",
        "source.nts.vat.filing-duty",
        "source.nts.business-registration.application"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-base",
      "title": "과세표준",
      "type": "term",
      "description": "세율 적용과 세액 산출의 기준이 되는 과세대상의 수량 또는 가액입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-credit",
      "title": "세액공제",
      "type": "term",
      "description": "산출세액에서 직접 차감하는 공제입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.year-end-settlement.special-credit"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-law",
      "title": "세법",
      "type": "term",
      "description": "국세의 종목과 세율을 정하는 법률과 국세기본법이 세법으로 묶는 관련 법률 체계입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-period",
      "title": "과세기간",
      "type": "term",
      "description": "세법에 따라 과세표준 계산의 기초가 되는 기간입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-rate",
      "title": "세율",
      "type": "term",
      "description": "과세표준 또는 공급가액 등에 적용해 산출세액을 계산하는 비율입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.income-tax.rates",
        "source.nts.corporate-tax.rates"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.tax-reduction",
      "title": "세액감면",
      "type": "term",
      "description": "정책 목적에 따라 산출세액 또는 납부할 세액을 줄여 주는 조세지원입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.year-end-settlement.calculation",
        "source.nts.corporate-tax.reliefs"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.total-income",
      "title": "총소득",
      "type": "term",
      "description": "근로·자녀장려금 자격 판정에서 근로, 사업, 종교인, 기타, 이자·배당·연금소득을 합산한 금액입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.grant.eligibility"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.withholding",
      "title": "원천징수",
      "type": "term",
      "description": "소득을 지급하는 자가 세법에 따라 세금을 미리 징수해 납부하는 방식입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.national-tax-framework-act.2026.article2",
        "source.nts.year-end-settlement.calculation"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    },
    {
      "id": "term.withholding-obligor",
      "title": "원천징수의무자",
      "type": "term",
      "description": "원천징수 대상 소득 또는 수입금액을 지급하면서 세액을 징수·신고·납부해야 하는 개인이나 법인입니다.",
      "folder": "40_Terms",
      "basis_year": 2026,
      "effective_date": null,
      "expiration_date": null,
      "parents": [],
      "children": [],
      "related": [],
      "terms": [],
      "deadlines": [],
      "sources": [
        "source.nts.withholding.overview"
      ],
      "law_reference": "",
      "tags": [
        "term"
      ]
    }
  ]
};

(() => {
  const items = ONTOLOGY_DATA.items;
  const byId = new Map(items.map((item) => [item.id, item]));
  const typeLabels = ONTOLOGY_DATA.type_labels;
  const typeRoles = ONTOLOGY_DATA.type_roles;
  const searchInput = document.querySelector("[data-search]");
  const listEl = document.querySelector("[data-item-list]");
  const tabsEl = document.querySelector("[data-tabs]");
  const resultCountEl = document.querySelector("[data-result-count]");
  const detailEl = document.querySelector("[data-detail-panel]");
  const sourceListEl = document.querySelector("[data-source-list]");
  const typeTableEl = document.querySelector("[data-type-table]");

  const state = {
    tab: "all",
    query: "",
    selectedId: "kr-tax-system"
  };

  const tabs = [
    { id: "all", label: "전체", test: () => true },
    { id: "taxes", label: "세목", test: (item) => item.type === "tax" || hasAncestor(item, "category.national-taxes") || hasAncestor(item, "category.local-taxes") || hasAncestor(item, "category.customs") },
    { id: "reliefs", label: "공제·감면", test: (item) => ["deduction", "tax-credit", "tax-reduction", "corporate-tax-support"].includes(item.type) || hasAncestor(item, "category.deductions-and-reliefs") },
    { id: "supports", label: "정책지원", test: (item) => item.type === "support-program" || hasAncestor(item, "category.policy-supports") },
    { id: "business", label: "사업자", test: (item) => hasAncestor(item, "category.business-tax-compliance") },
    { id: "filing", label: "신고기한", test: (item) => ["filing", "deadline"].includes(item.type) || hasAncestor(item, "category.filing-calendar") },
    { id: "terms", label: "용어·기준", test: (item) => ["term", "concept"].includes(item.type) },
    { id: "sources", label: "출처", test: (item) => item.type === "source" }
  ];

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function itemText(item) {
    return [
      item.id,
      item.title,
      typeLabels[item.type] || item.type,
      item.description,
      JSON.stringify(item.criteria || []),
      item.law_reference,
      item.publisher,
      item.url,
      ...(item.tags || [])
    ].join(" ").toLowerCase();
  }

  function hasAncestor(item, ancestorId, visited = new Set()) {
    if (!item || visited.has(item.id)) return false;
    visited.add(item.id);
    if ((item.parents || []).includes(ancestorId)) return true;
    return (item.parents || []).some((parentId) => hasAncestor(byId.get(parentId), ancestorId, visited));
  }

  function filteredItems() {
    const query = state.query.trim().toLowerCase();
    const activeTab = tabs.find((tab) => tab.id === state.tab) || tabs[0];
    return items
      .filter((item) => activeTab.test(item))
      .filter((item) => !query || itemText(item).includes(query))
      .sort((a, b) => {
        if (a.type === "domain") return -1;
        if (b.type === "domain") return 1;
        if (a.type !== b.type) return a.type.localeCompare(b.type);
        return a.title.localeCompare(b.title, "ko");
      });
  }

  function ensureVisibleSelection(visible) {
    if (!visible.length) {
      state.selectedId = "";
      return;
    }

    if (!visible.some((item) => item.id === state.selectedId)) {
      state.selectedId = visible[0].id;
    }
  }

  function renderTabs() {
    tabsEl.innerHTML = tabs
      .map((tab) => `<button class="tab-button" type="button" role="tab" aria-selected="${tab.id === state.tab}" data-tab="${tab.id}">${escapeHtml(tab.label)}</button>`)
      .join("");
  }

  function renderList() {
    const visible = filteredItems();
    ensureVisibleSelection(visible);
    resultCountEl.textContent = `${visible.length.toLocaleString("ko-KR")}개 표시`;
    if (!visible.length) {
      listEl.innerHTML = `<div class="empty-state">검색 조건에 맞는 항목이 없습니다.</div>`;
      return;
    }

    listEl.innerHTML = visible
      .map((item) => `
        <button class="item-row${item.id === state.selectedId ? " active" : ""}" type="button" data-select-item="${escapeHtml(item.id)}">
          <span>
            <strong>${escapeHtml(item.title)}</strong>
            <p>${escapeHtml(item.description)}</p>
          </span>
          <span class="type-chip">${escapeHtml(typeLabels[item.type] || item.type)}</span>
        </button>
      `)
      .join("");
  }

  function relationBlock(title, ids) {
    const links = (ids || [])
      .map((id) => byId.get(id))
      .filter(Boolean)
      .map((item) => `<button class="relation-link" type="button" data-select-item="${escapeHtml(item.id)}">${escapeHtml(item.title)}</button>`)
      .join("");

    if (!links) return "";
    return `
      <div class="relation-group">
        <h4>${escapeHtml(title)}</h4>
        <div class="relation-links">${links}</div>
      </div>
    `;
  }

  function sourceBlock(ids) {
    const links = (ids || [])
      .map((id) => byId.get(id))
      .filter(Boolean)
      .map((source) => {
        if (source.url) {
          return `<a class="relation-link" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.title)}</a>`;
        }
        return `<span class="relation-link">${escapeHtml(source.title)}</span>`;
      })
      .join("");
    if (!links) return "";
    return `
      <div class="relation-group">
        <h4>근거·출처</h4>
        <div class="relation-links">${links}</div>
      </div>
    `;
  }

  function formatKrw(value) {
    if (value === undefined || value === null || value === "") return "";
    const number = Number(value);
    return Number.isFinite(number) ? `${number.toLocaleString("ko-KR")}원` : String(value);
  }

  function formatPercent(value) {
    if (value === undefined || value === null || value === "") return "";
    return `${value}%`;
  }

  function criteriaBlock(criteria) {
    if (!criteria || !criteria.length) return "";
    const labels = {
      basis: "기준항목",
      condition: "조건",
      threshold_krw_min: "하한",
      threshold_krw: "기준금액",
      threshold_krw_max: "상한",
      rate_percent: "세율",
      rate_percent_min: "최저세율",
      rate_percent_max: "최고세율",
      progressive_deduction_krw: "누진공제",
      deduction_krw: "공제액",
      limit_krw: "한도",
      amount_krw: "금액",
      max_amount_krw: "최대금액",
      benefit: "혜택",
      note: "비고"
    };
    const orderedKeys = [
      "basis",
      "condition",
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
      "max_amount_krw",
      "benefit",
      "note"
    ];
    const items = criteria.map((criterion) => {
      const detail = orderedKeys
        .filter((key) => criterion[key] !== undefined && criterion[key] !== null && criterion[key] !== "")
        .map((key) => {
          let value = criterion[key];
          if (key.endsWith("_krw")) value = formatKrw(value);
          if (key.startsWith("rate_percent")) value = formatPercent(value);
          let label = labels[key] || key;
          if (key.startsWith("rate_percent") && criterion.rate_label) {
            label = key === "rate_percent_min" ? `최저${criterion.rate_label}` : key === "rate_percent_max" ? `최고${criterion.rate_label}` : criterion.rate_label;
          }
          return `<span>${escapeHtml(label)}: <strong>${escapeHtml(value)}</strong></span>`;
        })
        .join("");
      const source = criterion.source ? byId.get(criterion.source) : null;
      const sourceLink = source ? `<button class="relation-link" type="button" data-select-item="${escapeHtml(source.id)}">${escapeHtml(source.title)}</button>` : "";
      return `
        <li>
          <strong>${escapeHtml(criterion.label || "기준")}</strong>
          <div>${detail}</div>
          ${sourceLink ? `<p>${sourceLink}</p>` : ""}
        </li>
      `;
    }).join("");
    return `
      <div class="criteria-block">
        <h4>기준 내역</h4>
        <ul>${items}</ul>
      </div>
    `;
  }

  function renderDetail() {
    const item = byId.get(state.selectedId) || byId.get("kr-tax-system") || items[0];
    if (!item) {
      detailEl.innerHTML = `
        <div class="detail-kicker">검색 결과 없음</div>
        <h3>선택할 항목이 없습니다</h3>
        <p>검색어를 줄이거나 다른 필터를 선택해 주세요.</p>
      `;
      return;
    }
    const relationHtml = [
      relationBlock("상위 항목", item.parents),
      relationBlock("하위 항목", item.children),
      relationBlock("관련 항목", item.related),
      relationBlock("관련 용어", item.terms),
      relationBlock("관련 기한", item.deadlines),
      sourceBlock(item.sources)
    ].filter(Boolean).join("");
    const criteriaHtml = criteriaBlock(item.criteria);

    detailEl.innerHTML = `
      <div class="detail-kicker">${escapeHtml(typeLabels[item.type] || item.type)} · ${escapeHtml(item.id)}</div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.description)}</p>
      <div class="meta-grid">
        <div><span>기준연도</span><strong>${escapeHtml(item.basis_year || "해당 없음")}</strong></div>
        <div><span>법령 근거</span><strong>${escapeHtml(item.law_reference || "출처 노드 참조")}</strong></div>
        <div><span>폴더</span><strong>${escapeHtml(item.folder || "-")}</strong></div>
        <div><span>태그</span><strong>${escapeHtml((item.tags || []).join(", ") || "-")}</strong></div>
      </div>
      ${criteriaHtml}
      <div class="relations">${relationHtml || "<p>연결된 관계가 없습니다.</p>"}</div>
    `;
  }

  function renderTypeTable() {
    const counts = ONTOLOGY_DATA.summary.type_counts;
    typeTableEl.innerHTML = Object.keys(counts)
      .sort((a, b) => (typeLabels[a] || a).localeCompare(typeLabels[b] || b, "ko"))
      .map((type) => `
        <tr>
          <td><strong>${escapeHtml(typeLabels[type] || type)}</strong><br><span>${escapeHtml(type)}</span></td>
          <td>${Number(counts[type]).toLocaleString("ko-KR")}</td>
          <td>${escapeHtml(typeRoles[type] || "온톨로지 노드")}</td>
        </tr>
      `)
      .join("");
  }

  function renderSources() {
    const sources = items
      .filter((item) => item.type === "source")
      .sort((a, b) => (a.publisher || "").localeCompare(b.publisher || "", "ko") || a.title.localeCompare(b.title, "ko"));

    sourceListEl.innerHTML = sources
      .map((source) => `
        <article class="source-card">
          <span>${escapeHtml(source.publisher || "공식 출처")} · ${escapeHtml(source.basis_date || ONTOLOGY_DATA.basis_date)}</span>
          <strong>${escapeHtml(source.title)}</strong>
          <p>${escapeHtml(source.description)}</p>
          ${source.url ? `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">원문 열기</a>` : ""}
        </article>
      `)
      .join("");
  }

  function downloadJson() {
    const exportData = {
      version: ONTOLOGY_DATA.version,
      basis_date: ONTOLOGY_DATA.basis_date,
      manifests: ONTOLOGY_DATA.manifests,
      items: ONTOLOGY_DATA.items
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "opentax-2026.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  document.addEventListener("click", (event) => {
    const selectButton = event.target.closest("[data-select-item]");
    if (selectButton) {
      const id = selectButton.getAttribute("data-select-item");
      if (byId.has(id)) {
        state.selectedId = id;
        renderList();
        renderDetail();
        document.querySelector("#browser")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    const tabButton = event.target.closest("[data-tab]");
    if (tabButton) {
      state.tab = tabButton.getAttribute("data-tab");
      renderTabs();
      renderList();
      renderDetail();
    }

    if (event.target.closest("[data-download-json]")) {
      downloadJson();
    }
  });

  searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderList();
    renderDetail();
  });

  renderTypeTable();
  renderSources();
  renderTabs();
  renderList();
  renderDetail();
})();
