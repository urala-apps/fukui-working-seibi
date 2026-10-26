-- 働く環境整備補助金・奨励金のチャット（working-chat）用の表
-- 同じ Supabase プロジェクトの補助金ボット（chat_*）とは表を分ける

-- お客さんごとの月の利用回数
create table if not exists public.working_chat_usage (
  bot   text not null,
  month text not null,          -- 例 2026-10
  count integer not null default 0,
  primary key (bot, month)
);
alter table public.working_chat_usage enable row level security;

-- 1回数えて、数えたあとの回数を返す（Edge Function から service_role で呼ぶ）
create or replace function public.working_chat_count(p_bot text, p_month text)
returns integer language sql security definer set search_path = public as $$
  insert into working_chat_usage (bot, month, count) values (p_bot, p_month, 1)
  on conflict (bot, month) do update set count = working_chat_usage.count + 1
  returning count;
$$;

-- 公開しない参考メモ（AI だけが読む。個人名・会社名を除いて表に直接入れる）
create table if not exists public.working_chat_notes (
  bot        text primary key,
  body       text not null,
  updated_at timestamptz not null default now()
);
alter table public.working_chat_notes enable row level security;

-- 質問と答えの記録（電話番号・メールアドレスは Edge Function で伏せ字にしてから入れる）
create table if not exists public.working_chat_logs (
  id         bigint generated always as identity primary key,
  bot        text not null,
  session    text not null,          -- 小窓を開くごとのランダムな番号
  topics     text[] not null default '{}',  -- 答えに使った助成金の番号
  question   text not null,
  answer     text not null,
  src        text not null default '',
  choices    jsonb not null default '[]'::jsonb,
  handoff    boolean not null default false,
  created_at timestamptz not null default now()
);
create index if not exists working_chat_logs_bot_created on public.working_chat_logs (bot, created_at desc);
alter table public.working_chat_logs enable row level security;

-- 権限：サイトからは直接触らせない。Edge Function（service_role）だけ
revoke all on public.working_chat_usage from anon, authenticated;
revoke all on public.working_chat_notes from anon, authenticated;
revoke all on public.working_chat_logs from anon, authenticated;
grant select, insert, update on public.working_chat_usage to service_role;
grant select, insert, update on public.working_chat_notes to service_role;
grant select, insert on public.working_chat_logs to service_role;
revoke execute on function public.working_chat_count(text, text) from public, anon, authenticated;
grant execute on function public.working_chat_count(text, text) to service_role;
