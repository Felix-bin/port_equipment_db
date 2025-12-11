import { mergeConfig } from 'vite';
import eslint from 'vite-plugin-eslint';
import baseConfig from './vite.config.base';

export default mergeConfig(
  {
    mode: 'development',
    server: {
      host: '0.0.0.0', // 允许外部访问
      port: 5173, // 指定端口
      open: true,
      fs: {
        strict: true,
      },
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    plugins: [
      eslint({
        cache: false,
        include: ['src/**/*.ts', 'src/**/*.tsx', 'src/**/*.vue'],
        exclude: ['node_modules'],
        emitWarning: false, // 禁用警告输出，避免控制台被 prettier 警告淹没
        failOnError: false, // 不因 ESLint 错误而中断构建
        failOnWarning: false, // 不因 ESLint 警告而中断构建
      }),
    ],
  },
  baseConfig
);
