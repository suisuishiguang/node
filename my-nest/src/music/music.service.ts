import { Injectable, Inject, HttpService } from '@nestjs/common';
import { Model } from 'mongoose';
import { map } from 'rxjs/internal/operators/map';

@Injectable()
export class MusicService {
    constructor(
        @Inject('MusicModelToken') private readonly MusicModel: Model<any>,
        private readonly httpService: HttpService,
    ) { }

    /**
     * qq 音乐
     */
    // 常量
    private qq_common_param = {
        g_tk: 5381,
        inCharset: 'utf-8',
        outCharset: 'utf-8',
        platform: 'yqq',
        notice: 0,
        needNewCode: 0,
        loginUin: 0,
        hostUin: 0,
    };

    // 轮播图
    private qqCarouselUrl = 'https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg';
    async qqCarousel(): Promise<any> {
        const url = this.qqCarouselUrl;

        return this.httpService.get(url).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 歌单列表
    private qqSongListUrl = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg';
    async qqSongList(): Promise<any> {
        const url = this.qqSongListUrl;
        const params = Object.assign({}, this.qq_common_param, {
            format: 'json',
            categoryId: 10000000,
            sortId: 5,
            sin: 0,
            ein: 19,
        });

        return this.httpService.get(url, {
            headers: {
              referer: 'https://y.qq.com/portal/playlist.html',
            },
            params,
          }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 歌单详情
    private qqSongListDetailUrl = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg';
    async qqSongListDetail(request): Promise<any> {
        const url = this.qqSongListDetailUrl;
        const params = Object.assign({}, this.qq_common_param, {
            format: 'json',
            type: 1,
            json: 1,
            utf8: 1,
            onlysong: 0,
            disstid: request.disstid || '5621494294',
        });

        return this.httpService.get(url, {
            headers: {
              referer: `https://y.qq.com/n/yqq/playsquare/${request.disstid || '5621494294'}.html`,
            },
            params,
          }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 歌手数据
    private qqSingerUrl = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg';
    async qqSinger(request): Promise<any> {
        const url = this.qqSingerUrl;
        const params = Object.assign({}, this.qq_common_param, {
            pagenum: 1,
            pagesize: 100,
            format: 'jsonp',
            channel: 'singer',
            page: 'list',
            key: request.key || 'cn_woman_all', // cn_woman_all j_woman_all
        });

        return this.httpService.get(url, {
            params,
        }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 歌手详情
    private qqSingerDetailUrl = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg';
    async qqSingerDetail(request): Promise<any> {
        const url = this.qqSingerDetailUrl;

        const params = Object.assign({}, this.qq_common_param, {
            begin: 0,
            num: 50,
            format: 'jsonp',
            order: 'listen',
            songstatus: 1,
            singermid: request.fsinger_mid || '001fNHEf1SFEFN',
        });

        return this.httpService.get(url, {
            params,
        }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 排行榜
    private qqRankUrl = 'https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg';
    async qqRank(request): Promise<any> {
        const url = this.qqRankUrl;

        const params = Object.assign({}, this.qq_common_param, {
            uin: 0,
            platform: 'h5',
            needNewCode: 1,
            param: 'json',
            format: 'json',
        });

        return this.httpService.get(url, {
            params,
        }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }

    // 排行榜详情
    private qqRankDetailUrl = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg';
    async qqRankDetail(request): Promise<any> {
        const url = this.qqRankDetailUrl;

        const params = Object.assign({}, this.qq_common_param, {
            uin: 0,
            tpl: 3,
            needNewCode: 1,
            type: 'top',
            page: 'detail',
            platform: 'h5',
            topid: request.id || '28',
        });

        return this.httpService.get(url, {
            params,
        }).pipe(map((resp: any) => {
            return resp.data;
        }));
    }
}
