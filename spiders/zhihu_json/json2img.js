/**
 * Created by qieguo on 2016/9/30.
 */
'use strict';

const spider = require('./lib/zhihu');
const logger = require('./lib/logger');

logger.debug('======  start spider  ======\r\n');


// startLoad������ͼƬ�ĺ�����
// ������json�ļ���û���ص�ͼƬ�Ļ�������ֱ��ʹ������ĺ�������ͼƬ��
spider.startLoad(function (err) {
  if (err) {
    logger.error('load images fail:', err);
  } else {
    logger.debug('\r\n======  finish load all images  ======');
  }
});
