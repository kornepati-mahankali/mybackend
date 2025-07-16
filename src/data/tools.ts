import { Tool } from '../types';

export const tools: Tool[] = [
  {
    id: '1',
    name: 'Gem Portal Scraper',
    category: 'gem',
    description: 'Extract tender data from Government e-Marketplace portal',
    states: ['Delhi', 'Mumbai', 'Chennai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'],
    icon: 'gem'
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