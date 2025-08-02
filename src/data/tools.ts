import { Tool } from '../types';

export const tools: Tool[] = [
  {
    id: '1',
    name: 'gem',
    category: 'gem',
    description: 'Scrapes data from the GEM website and generates Excel files for each page. Creates \'gem/scrapedfiles\' directory structure.',
    icon: 'gem',
    valid_states: [
      "ANDAMAN & NICOBAR", "ANDHRA PRADESH", "ARUNACHAL PRADESH", "ASSAM", "BIHAR",
      "CHANDIGARH", "CHHATTISGARH", "DADRA & NAGAR HAVELI", "DAMAN & DIU", "DELHI",
      "GOA", "GUJARAT", "HARYANA", "HIMACHAL PRADESH", "JAMMU & KASHMIR", "JHARKHAND",
      "KARNATAKA", "KERALA", "LAKSHADWEEP", "MADHYA PRADESH", "MAHARASHTRA", "MANIPUR",
      "MEGHALAYA", "MIZORAM", "NAGALAND", "ODISHA", "PUDUCHERRY", "PUNJAB", "RAJASTHAN",
      "SIKKIM", "TAMIL NADU", "TELANGANA", "TRIPURA", "UTTAR PRADESH", "UTTARAKHAND", "WEST BENGAL"
    ],
    valid_cities: {
      "ANDAMAN & NICOBAR": ["NICOBAR", "NORTH AND MIDDLE ANDAMAN", "SOUTH ANDAMAN"],
      "ANDHRA PRADESH": ["ANANTHAPUR", "CHITTOOR", "CUDDAPAH", "EAST GODAVARI", "GUNTUR", "KRISHNA", "KURNOOL", "NELLORE", "PRAKASAM", "SRIKAKULAM", "VISAKHAPATNAM", "VIZIANAGARAM", "WEST GODAVARI"],
      "ARUNACHAL PRADESH": ["CHANGLANG", "DIBANG VALLEY", "EAST KAMENG", "EAST SIANG", "KURUNG KUMEY", "LOHIT", "LOWER SUBANSIRI", "PAPUM PARE", "TAWANG", "TIRAP", "UPPER SIANG", "UPPER SUBANSIRI", "WEST KAMENG", "WEST SIANG"],
      "ASSAM": ["BARPETA", "BONGAIGAON", "CACHAR", "DARRANG", "DHEMAJI", "DHUBRI", "DIBRUGARH", "GOALPARA", "GOLAGHAT", "HAILAKANDI", "JORHAT", "KAMRUP", "KARBI ANGLONG", "KARIMGANJ", "KOKRAJHAR", "LAKHIMPUR", "MARIGAON", "NAGAON", "NALBARI", "NORTH CACHAR HILLS", "SIVASAGAR", "SONITPUR", "TINSUKIA"],
      "BIHAR": ["ARARIA", "ARWAL", "AURANGABAD", "BANKA", "BEGUSARAI", "BHAGALPUR", "BHOJPUR", "BUXAR", "DARBHANGA", "EAST CHAMPARAN", "GAYA", "GOPALGANJ", "JAMUI", "JEHANABAD", "KAIMUR (BHABUA)", "KATIHAR", "KHAGARIA", "KISHANGANJ", "LAKHISARAI", "MADHEPURA", "MADHUBANI", "MUNGER", "MUZAFFARPUR", "NALANDA", "NAWADA", "PATNA", "PURNIA", "ROHTAS", "SAHARSA", "SAMASTIPUR", "SARAN", "SHEIKHPURA", "SHEOHAR", "SITAMARHI", "SIWAN", "SUPAUL", "VAISHALI", "WEST CHAMPARAN"],
      "CHANDIGARH": ["CHANDIGARH"],
      "CHHATTISGARH": ["BASTAR", "BIJAPUR", "BILASPUR", "DANTEWADA", "DHAMTARI", "DURG", "JANJGIR-CHAMPA", "JASHPUR", "KANKER", "KAWARDHA", "KORBA", "KORIYA", "MAHASAMUND", "RAIGARH", "RAIPUR", "RAJNANDGAON", "SURGUJA"],
      "DADRA & NAGAR HAVELI": ["DADRA & NAGAR HAVELI"],
      "DAMAN & DIU": ["DAMAN", "DIU"],
      "DELHI": ["CENTRAL DELHI", "EAST DELHI", "NEW DELHI", "NORTH DELHI", "NORTH EAST DELHI", "NORTH WEST DELHI", "SHAHDARA", "SOUTH DELHI", "SOUTH EAST DELHI", "SOUTH WEST DELHI", "WEST DELHI"],
      "GOA": ["NORTH GOA", "SOUTH GOA"],
      "GUJARAT": ["AHMEDABAD", "AMRELI", "ANAND", "BANASKANTHA", "BHARUCH", "BHAVNAGAR", "DAHOD", "GANDHI NAGAR", "JAMNAGAR", "JUNAGADH", "KACHCHH", "KHEDA", "MAHESANA", "NARMADA", "NAVSARI", "PANCH MAHALS", "PATAN", "PORBANDAR", "RAJKOT", "SABARKANTHA", "SURAT", "SURENDRA NAGAR", "THE DANGS", "VADODARA", "VALSAD"],
      "HARYANA": ["AMBALA", "BHIWANI", "FARIDABAD", "FATEHABAD", "GURGAON", "HISAR", "JHAJJAR", "JIND", "KAITHAL", "KARNAL", "KURUKSHETRA", "MAHENDRAGARH", "PANCHKULA", "PANIPAT", "REWARI", "ROHTAK", "SIRSA", "SONIPAT", "YAMUNA NAGAR"],
      "HIMACHAL PRADESH": ["BILASPUR (HP)", "CHAMBA", "HAMIRPUR", "KANGRA", "KINNAUR", "KULLU", "LAHUL & SPITI", "MANDI", "SHIMLA", "SIRMAUR", "SOLAN", "UNA"],
      "JAMMU & KASHMIR": ["ANANTHNAG", "BANDIPUR", "BARAMULLA", "BUDGAM", "DODA", "JAMMU", "KARGIL", "KATHUA", "KUPWARA", "LEH", "POONCH", "PULWAMA", "RAJAURI", "SAMBA", "SRINAGAR", "UDHAMPUR"],
      "JHARKHAND": ["BOKARO", "CHATRA", "DEOGHAR", "DHANBAD", "DUMKA", "EAST SINGHBHUM", "GARHWA", "GIRIDH", "GODDA", "GUMLA", "HAZARIBAG", "JAMTARA", "KHUNTI", "KODERMA", "LATEHAR", "LOHARDAGA", "PAKUR", "PALAMAU", "RAMGARH", "RANCHI", "SAHIBGANJ", "SARAIKELA KHARSAWAN", "SIMDEGA", "WEST SINGHBHUM"],
      "KARNATAKA": ["BAGALKOT", "BANGALORE", "BANGALORE RURAL", "BELGAUM", "BELLARY", "BIDAR", "BIJAPUR", "CHAMRAJNAGAR", "CHICKMAGALUR", "CHIKKABALLAPUR", "CHITRADURGA", "DAKSHINA KANNADA", "DAVANGARE", "DHARWARD", "GADAG", "GULBARGA", "HASSAN", "HAVERI", "KODAGU", "KOLAR", "KOPPAL", "MANDYA", "MYSURU", "RAICHUR", "RAMANAGAR", "SHIMOGA", "TUMKUR", "UDUPI", "UTTARA KANNADA"],
      "KERALA": ["ALAPPUZHA", "ERNAKULAM", "IDUKKI", "KANNUR", "KASARGOD", "KOLLAM", "KOTTAYAM", "KOZHIKODE", "MALAPPURAM", "PALAKKAD", "PATHANAMTHITTA", "THIRUVANANTHAPURAM", "THRISSUR", "WAYANAD"],
      "LAKSHADWEEP": ["LAKSHADWEEP"],
      "MADHYA PRADESH": ["ANUPPUR", "ASHOKNAGAR", "BALAGHAT", "BARWANI", "BETUL", "BHIND", "BHOPAL", "CHHATARPUR", "CHHINDWARA", "DAMOH", "DATIA", "DEWAS", "DHAR", "DINDORI", "GUNA", "HARDa", "HOSHANGABAD", "INDORE", "JABALPUR", "KATNI", "MANDLA", "MANDSAUR", "MORENA", "NARMADAPURAM", "NEEMUCH", "PANCHMADHI", "RAISEN", "RAJGARH", "RATLAM", "REWA", "SAGAR", "SATNA", "SEHORE", "SHIVPURI", "SIDHI", "TIKAMGARH", "UMARIA", "VIDISHA"],
      "MAHARASHTRA": ["AHMADNAGAR", "AKOLA", "AMRAVATI", "AURANGABAD", "BANDRA", "BEED", "BULDHANA", "CHANDRAPUR", "DHULE", "GADCHIROLI", "GONDIA", "HINGOLI", "JALNA", "JALGAON", "KOLHAPUR", "LATUR", "NANDURBAR", "NASHIK", "OSMANABAD", "PARBHANI", "PUNE", "RAIGAD", "RATNAGIRI", "SANGLI", "SATARA", "SINDHUDURG", "SOLAPUR", "THANE", "WASHIM", "YAVATMAL"],
      "MANIPUR": ["BISHNUPUR", "CHURACHANDPUR", "CHAMPHAI", "IMPHAL EAST", "IMPHAL WEST", "JIRIBAM", "KANGPOKPI", "KAKCHING", "NONEY", "PHEK", "SENAPATI", "TAMENGLONG", "THOUBAL", "UKHRUL"],
      "MEGHALAYA": ["EAST GARO HILLS", "EAST KHASI HILLS", "NORTH GARO HILLS", "RIBHOI", "SOUTH GARO HILLS", "SOUTH KHASI HILLS", "WEST GARO HILLS", "WEST KHASI HILLS"],
      "MIZORAM": ["AIZAWL", "CHAMPHAI", "KHAWZAWL", "LUNGLEI", "MAMIT", "SAIHA", "SIAHA", "THANHLUN"],
      "NAGALAND": ["DIMAPUR", "KIPHIRE", "MOKOKCHUNG", "MON", "PHEK", "TUENSANG", "WOKHA", "ZUNHEBOTO"],
      "ODISHA": ["ANGUL", "BALASORE", "BARGARH", "BHADRAK", "BOLANGIR", "DEOGARH", "Dhenkanal", "Ganjam", "Ganjam", "Kandhamal", "Kendrapara", "Kendujhar", "Khurda", "Malkangiri", "Nabarangpur", "Nayagarh", "Nuapada", "Rayagada", "Sambalpur", "Sonepur", "Jagatsinghpur", "Jharsuguda", "Kandhamal", "Mayurbhanj"],
      "PUDUCHERRY": ["PUDUCHERRY"],
      "PUNJAB": ["AMRITSAR", "BARNALA", "BATALA", "FATEHGARH SAHIB", "FARIDKOT", "GURDASPUR", "HOSHIARPUR", "JALANDHAR", "KAPURTHALA", "LUDHIANA", "MANSA", "MOGA", "PATHANKOT", "PATIALA", "RUPNAGAR", "SANGRUR", "SAS NAGAR", "TARN TARAN"],
      "RAJASTHAN": ["AJMER", "ALWAR", "BANSWARA", "BARAN", "BARMER", "BHARATPUR", "BHILWARA", "BIKANER", "CHITTORGARH", "CHURU", "DHAULPUR", "DUNGARPUR", "GANGANAGAR", "JAIL", "JAISALMER", "JAIPUR", "JODHPUR", "KARAULI", "KOTA", "NAGAUR", "PALI", "RAJSAMAND", "SAWAI MADHOPUR", "SIKAR", "TONK", "UDAIPUR"],
      "SIKKIM": ["EAST SIKKIM", "NORTH SIKKIM", "SOUTH SIKKIM", "WEST SIKKIM"],
      "TAMIL NADU": ["ARIYALUR", "CHENNAI", "CHENNAI (TOWN)", "COIMBATORE", "CUDDALORE", "DINDIGUL", "ERODE", "KANCHEEPURAM", "KARUR", "MADURAI", "NAGAPATTINAM", "NAMAKKAL", "PERAMBALUR", "PUDUKOTTAI", "RAMANATHAPURAM", "SALEM", "SIVAGANGA", "TIRUCHIRAPALLI", "TIRUNELVELI", "VILLUPURAM", "VIRUDHUNAGAR"],
      "TELANGANA": ["ADILABAD", "HYDERABAD", "KHAMMAM", "MAHABUBNAGAR", "MEDAK", "NALGONDA", "NALGONDA", "NIZAMABAD", "RANGAREDDY", "WARANGAL"],
      "TRIPURA": ["AGARTALA", "DHALAI", "GOMATI", "KHOWAI", "NORTH TRIPURA", "SOUTH TRIPURA", "UNAKOTI"],
      "UTTAR PRADESH": ["AGRA", "ALIGARH", "ALLAHABAD", "AMBEDKAR NAGAR", "AMROHA", "AURAIYA", "BAHRAICH", "BANDA", "BULANDSHAHR", "CHANDAULI", "CHHATARPUR", "DEORIA", "ETAH", "ETAWAH", "FARRUKHABAD", "FATEHPUR", "GHAZIPUR", "GHAZIABAD", "GORAKHPUR", "HAMIRPUR", "HAPUR", "HARDOI", "JALAUN", "JHANSI", "KANNAUJ", "KASGANJ", "KAUSHAMBI", "KUSHINAGAR", "LUCKNOW", "MAIHAR", "MAU", "MEERUT", "MIRZAPUR", "MORADABAD", "MUZAFFARNAGAR", "PILIBHIT", "RAE BARELI", "RAMPUR", "SAHARANPUR", "SANT RAVIDAS NAGAR", "SHAMLI", "SHRAWASTI", "SITAPUR", "SONBHADRA", "SULTANPUR", "UNNAO", "VARANASI", "VAISHALI", "YAJMAAN"],
      "UTTARAKHAND": ["ALMORA", "BAGESHWER", "CHAMOLI", "CHAMPAWAT", "DEHRA DUN", "HARIDWAR", "NANITAL", "PITHORAGARH", "RUHAT", "TEHRI GARHWAL", "UTTARKASHI"],
      "WEST BENGAL": ["ALIPURDUAR", "BANKURA", "BARDHAMAN", "BIRBHUM", "DARBHANGA", "DEBAGRAM", "DINAJPUR", "HOOGHLY", "HOWRAH", "JALPAIGURI", "JHARGRAM", "KALIMPONG", "KOLKATA", "MALDAH", "MURSHIDABAD", "NADIA", "NORTH 24 PARGANAS", "PURBA BARDHAMAN", "PURBA MEDINIPUR", "SOUTH 24 PARGANAS", "PASCHIM BARDHAMAN", "PASCHIM MEDINIPUR", "BANKURA"]
    },
    inputs: [
      {
        name: 'startingpage',
        type: 'int',
        required: true,
        description: 'Starting Page Number'
      },
      {
        name: 'totalpages',
        type: 'int',
        required: true,
        description: 'Total Pages to Scrape'
      },
      {
        name: 'username',
        type: 'string',
        required: true,
        default: '',
        description: 'Username for GEM Portal'
      },

    ]
  },
  {
    id: '2',
    name: 'Gem Tender Analyzer',
    category: 'gem',
    description: 'Analyze and categorize GEM tender documents',
    valid_states: ['All India', 'North Zone', 'South Zone', 'East Zone', 'West Zone'],
    icon: 'analyze'
  },
  {
    id: '3',
    name: 'Global Trade Monitor',
    category: 'global',
    description: 'Monitor international trade opportunities',
    valid_states: ['USA', 'UK', 'Germany', 'France', 'Japan', 'Singapore', 'Australia', 'Canada'],
    icon: 'globe'
  },
  {
    id: '4',
    name: 'Market Intelligence Tool',
    category: 'global',
    description: 'Gather competitive intelligence from global markets',
    valid_states: ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Africa', 'Latin America'],
    icon: 'chart'
  },
  {
    id: '5',
    name: 'Universal Data Extractor',
    category: 'all',
    description: 'Extract data from any website or portal',
    valid_states: ['Custom URL', 'Predefined Sites', 'Social Media', 'News Sites', 'Government Portals'],
    icon: 'download'
  },
  {
    id: '6',
    name: 'Content Aggregator',
    category: 'all',
    description: 'Aggregate content from multiple sources',
    valid_states: ['Real-time', 'Scheduled', 'On-demand', 'Batch Processing'],
    icon: 'layers'
  },
  {
    id: '7',
    name: 'eprocurement',
    category: 'eprocurement',
    description: 'Scrapes data from the E-Procurement website and generates Excel files for each page.',
    valid_states: ['Central Govt', 'State Govt', 'PSU', 'Private', 'International'],
    icon: 'shopping-cart',
    inputs: [
      {
        name: 'base_url',
        type: 'string',
        required: true,
        default: '',
        description: 'Base URL for scraping'
      },
      {
        name: 'tender_type',
        type: 'string',
        required: true,
        default: 'O',
        description: 'Tender type (O/L)'
      },
      {
        name: 'days_interval',
        type: 'int',
        required: true,
        default: 7,
        description: 'How many days back to scrape'
      },
      {
        name: 'start_page',
        type: 'int',
        required: true,
        default: 1,
        description: 'Starting page number'
      }
    ]
  },
  {
    id: '8',
    name: 'E-Procurement Monitor',
    category: 'eprocurement',
    description: 'Monitor e-procurement platforms for new opportunities',
    valid_states: ['Central Govt', 'State Govt', 'PSU', 'Private', 'International'],
    icon: 'shopping-cart'
  },
  {
    id: '9',
    name: 'Bid Analytics Tool',
    category: 'eprocurement',
    description: 'Analyze bidding patterns and success rates',
    valid_states: ['Tender Analysis', 'Competitor Analysis', 'Price Analysis', 'Success Rate'],
    icon: 'target'
  },
  {
    id: '10',
    name: 'IREPS',
    category: 'ireps',
    description: 'Scrapes data from the IREPS (Indian Railways E-Procurement System) website and generates Excel files for each page.',
    valid_states: ['Central Govt', 'Railways', 'PSU', 'Private'],
    icon: 'layers',
    inputs: [
      {
        name: 'name',
        type: 'string',
        required: true,
        default: '',
        description: 'Name for the scraping session'
      },
      {
        name: 'startingpage',
        type: 'int',
        required: true,
        description: 'Starting Page Number'
      }
    ]
  }
];