import { Tool } from '../types';

export const tools: Tool[] = [
  {
    id: '1',
    name: 'Gem Portal Scraper',
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
      "DELHI": ["New Delhi", "Old Delhi", "Dwarka", "Rohini", "Pitampura"],
      "MAHARASHTRA": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik"],
      "TAMIL NADU": ["Chennai", "Coimbatore", "Madurai", "Salem", "Vellore"],
      "WEST BENGAL": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
      "KARNATAKA": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
      "TELANGANA": ["Hyderabad", "Warangal", "Karimnagar", "Nizamabad", "Adilabad"],
      "GUJARAT": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
      "UTTAR PRADESH": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Prayagraj"],
      "BIHAR": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia"],
      "ODISHA": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"]
    },
    inputs: [
      {
        name: 'startingpage',
        type: 'int',
        required: true,
        default: 1,
        description: 'Starting Page Number'
      },
      {
        name: 'totalpages',
        type: 'int',
        required: true,
        default: 5,
        description: 'Total Pages to Scrape'
      },
      {
        name: 'username',
        type: 'string',
        required: true,
        default: '',
        description: 'Username for GEM Portal'
      },
      {
        name: 'days_interval',
        type: 'int',
        required: true,
        default: 7,
        description: 'Days Interval for Search'
      }
    ]
  },
  {
    id: '2',
    name: 'Gem Tender Analyzer',
    category: 'gem',
    description: 'Analyze and categorize GEM tender documents',
    states: ['All India', 'North Zone', 'South Zone', 'East Zone', 'West Zone'],
    icon: 'analyze'
  },
  {
    id: '3',
    name: 'Global Trade Monitor',
    category: 'global',
    description: 'Monitor international trade opportunities',
    states: ['USA', 'UK', 'Germany', 'France', 'Japan', 'Singapore', 'Australia', 'Canada'],
    icon: 'globe'
  },
  {
    id: '4',
    name: 'Market Intelligence Tool',
    category: 'global',
    description: 'Gather competitive intelligence from global markets',
    states: ['North America', 'Europe', 'Asia Pacific', 'Middle East', 'Africa', 'Latin America'],
    icon: 'chart'
  },
  {
    id: '5',
    name: 'Universal Data Extractor',
    category: 'all',
    description: 'Extract data from any website or portal',
    states: ['Custom URL', 'Predefined Sites', 'Social Media', 'News Sites', 'Government Portals'],
    icon: 'download'
  },
  {
    id: '6',
    name: 'Content Aggregator',
    category: 'all',
    description: 'Aggregate content from multiple sources',
    states: ['Real-time', 'Scheduled', 'On-demand', 'Batch Processing'],
    icon: 'layers'
  },
  {
    id: '7',
    name: 'E-Procurement Monitor',
    category: 'eprocurement',
    description: 'Monitor e-procurement platforms for new opportunities',
    states: ['Central Govt', 'State Govt', 'PSU', 'Private', 'International'],
    icon: 'shopping-cart'
  },
  {
    id: '8',
    name: 'Bid Analytics Tool',
    category: 'eprocurement',
    description: 'Analyze bidding patterns and success rates',
    states: ['Tender Analysis', 'Competitor Analysis', 'Price Analysis', 'Success Rate'],
    icon: 'target'
  }
];