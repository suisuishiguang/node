import { Document } from 'mongoose';

export interface Stock extends Document {
    readonly address: string;
}
