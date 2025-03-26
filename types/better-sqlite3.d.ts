declare module "better-sqlite3" {
  interface Database {
    prepare(sql: string): Statement;
    exec(sql: string): void;
    close(): void;
  }

  interface Statement {
    run(...params: any[]): any;
    get(...params: any[]): any;
    all(...params: any[]): any[];
  }

  function Database(
    filename: string,
    options?: { readonly?: boolean }
  ): Database;
  export = Database;
}
