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
    icons: [
      { src: '/punchnotes_logo_48x48.png', sizes: '48x48', type: 'image/png' },
      { src: '/punchnotes_logo_96x96.png', sizes: '96x96', type: 'image/png' },
      { src: '/punchnotes_logo_144x144.png', sizes: '144x144', type: 'image/png' },
      { src: '/punchnotes_logo_180x180.png', sizes: '180x180', type: 'image/png' },
      { src: '/punchnotes_logo_192x192.png', sizes: '192x192', type: 'image/png' },
      { src: '/punchnotes_logo_512x512.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
