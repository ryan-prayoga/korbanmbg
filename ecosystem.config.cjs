module.exports = {
  apps: [
    {
      name: 'korbanmbg-api',
      script: './api/korbanmbg-api',
      cwd: '/home/ubuntu/projects/korbanmbg',
      env: {
        PORT: '8090',
        DB_HOST: 'localhost',
        DB_PORT: '5432',
        DB_USER: 'postgres',
        DB_PASS: 'P@ssw0rd18TraspaC',
        DB_NAME: 'korbanmbg',
      },
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
