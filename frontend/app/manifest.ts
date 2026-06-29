import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'PunchNotes',
    short_name: 'PunchNotes',
    description: 'Structured analysis of stand-up comedy sets',
    start_url: '/killtony',
    display: 'standalone',
    background_color: '#fafaf9',
    theme_color: '#ef372a',
    icons: [],
  };
}
