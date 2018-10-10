import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TestModule } from './test/test.module';
import { DatabaseModule } from './data-base/dataBase.module';
import { CatsModule } from './cats/cats.module';
import { PicModule } from './pic/pic.module';

@Module({
    imports: [
        TestModule,
        DatabaseModule,
        CatsModule,
        PicModule,
    ],
    controllers: [AppController],
    providers: [AppService],
})
export class AppModule {}

// export class AppModule implements NestModule {
//     configure(consumer: any): any {
//         consumer.apply([CorsMiddleware]).forRoutes({ path: '*', method: RequestMethod.ALL });
//     }
// }
