module.exports = {
  apps: [
    {
      name: 'korbanmbg-api',
      script: './api/start.sh',
      cwd: '/home/ubuntu/projects/korbanmbg',
    },
    {
      name: 'korbanmbg-web',
      script: './web/build/index.js',
      cwd: '/home/ubuntu/projects/korbanmbg',
      env: {
        PORT: '8091',
        ORIGIN: 'https://korbanmbg.ryanprayoga.dev',
      },
    },
  ],
};
