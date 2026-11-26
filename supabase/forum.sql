-- Teman Mama forum ("Tanya ibu-ibu") - run ONCE in Supabase: Dashboard > SQL Editor > New query > paste all > Run.
-- Visitors never write to tables directly: every write goes through the functions below, which check lengths,
-- block links / phone numbers / IC numbers, limit how often one device can post, and hide a post after 3 reports.
-- Moderation: Dashboard > Table Editor > questions / answers. Set hidden = false (and reports = 0) to restore a post,
-- or delete the row to remove it for good.

create table if not exists public.questions (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  topic       text not null check (topic in ('hamil', 'bersalin', 'pantang', 'bayi', 'menyusu', 'lain')),
  title       text not null check (char_length(title) between 8 and 140),
  body        text not null default '' check (char_length(body) <= 2000),
  nickname    text not null default 'Ibu' check (char_length(nickname) between 1 and 30),
  lang        text not null default 'ms' check (lang in ('ms', 'en')),
  device      text not null check (char_length(device) between 8 and 64),
  up          int  not null default 0,
  down        int  not null default 0,
  score       int  generated always as (up - down) stored,
  answers     int  not null default 0,
  reports     int  not null default 0,
  hidden      boolean not null default false
);

create table if not exists public.answers (
  id          bigint generated always as identity primary key,
  question_id bigint not null references public.questions (id) on delete cascade,
  created_at  timestamptz not null default now(),
  body        text not null check (char_length(body) between 2 and 2000),
  nickname    text not null default 'Ibu' check (char_length(nickname) between 1 and 30),
  device      text not null check (char_length(device) between 8 and 64),
  up          int  not null default 0,
  down        int  not null default 0,
  score       int  generated always as (up - down) stored,
  reports     int  not null default 0,
  hidden      boolean not null default false
);
create index if not exists answers_q_idx on public.answers (question_id);

create table if not exists public.votes (
  kind    text not null check (kind in ('q', 'a')),
  post_id bigint not null,
  device  text not null,
  value   smallint not null check (value in (-1, 1)),
  primary key (kind, post_id, device)
);

create table if not exists public.reports (
  kind       text not null check (kind in ('q', 'a')),
  post_id    bigint not null,
  device     text not null,
  created_at timestamptz not null default now(),
  primary key (kind, post_id, device)
);

-- Read access: only visible posts, and never the device column.
alter table public.questions enable row level security;
alter table public.answers   enable row level security;
alter table public.votes     enable row level security;
alter table public.reports   enable row level security;

drop policy if exists "read visible questions" on public.questions;
create policy "read visible questions" on public.questions for select to anon, authenticated using (hidden = false);
drop policy if exists "read visible answers" on public.answers;
create policy "read visible answers" on public.answers for select to anon, authenticated using (hidden = false);

revoke all on public.questions, public.answers, public.votes, public.reports from anon, authenticated;
grant select (id, created_at, topic, title, body, nickname, lang, up, down, score, answers, hidden) on public.questions to anon, authenticated;
grant select (id, question_id, created_at, body, nickname, up, down, score, hidden) on public.answers to anon, authenticated;

-- Shared checks ------------------------------------------------------------------------------------------
create or replace function public.tm_clean_text(p text) returns text
language plpgsql immutable set search_path = public as $$
begin
  if p ~* '(https?://|www\.|\.com\b|\.my\b|wa\.me|t\.me)' then raise exception 'no_links'; end if;
  if p ~ '(\+?6?0\s?1\d[\s-]?\d{3,4}[\s-]?\d{4})' then raise exception 'no_phone'; end if;
  if p ~ '\d{6}-?\d{2}-?\d{4}' then raise exception 'no_ic'; end if;
  return btrim(regexp_replace(p, '\s+', ' ', 'g'));
end $$;

-- Ask a question
create or replace function public.ask_question(p_topic text, p_title text, p_body text, p_nickname text, p_lang text, p_device text)
returns bigint language plpgsql security definer set search_path = public as $$
declare new_id bigint;
begin
  if (select count(*) from questions where device = p_device and created_at > now() - interval '1 hour') >= 5 then
    raise exception 'slow_down';
  end if;
  insert into questions (topic, title, body, nickname, lang, device)
  values (p_topic, tm_clean_text(p_title), tm_clean_text(coalesce(p_body, '')),
          coalesce(nullif(tm_clean_text(coalesce(p_nickname, '')), ''), 'Ibu'), coalesce(p_lang, 'ms'), p_device)
  returning id into new_id;
  return new_id;
end $$;

-- Answer a question
create or replace function public.post_answer(p_question bigint, p_body text, p_nickname text, p_device text)
returns bigint language plpgsql security definer set search_path = public as $$
declare new_id bigint;
begin
  if not exists (select 1 from questions where id = p_question and hidden = false) then raise exception 'not_found'; end if;
  if (select count(*) from answers where device = p_device and created_at > now() - interval '1 hour') >= 20 then
    raise exception 'slow_down';
  end if;
  insert into answers (question_id, body, nickname, device)
  values (p_question, tm_clean_text(p_body), coalesce(nullif(tm_clean_text(coalesce(p_nickname, '')), ''), 'Ibu'), p_device)
  returning id into new_id;
  update questions set answers = answers + 1 where id = p_question;
  return new_id;
end $$;

-- Thumbs up (1), thumbs down (-1) or remove my vote (0). One vote per device per post.
create or replace function public.cast_vote(p_kind text, p_id bigint, p_device text, p_value int)
returns void language plpgsql security definer set search_path = public as $$
begin
  if p_kind not in ('q', 'a') or p_value not in (-1, 0, 1) or char_length(p_device) < 8 then raise exception 'bad_vote'; end if;
  if p_value = 0 then
    delete from votes where kind = p_kind and post_id = p_id and device = p_device;
  else
    insert into votes (kind, post_id, device, value) values (p_kind, p_id, p_device, p_value)
    on conflict (kind, post_id, device) do update set value = excluded.value;
  end if;
  if p_kind = 'q' then
    update questions set up = (select count(*) from votes where kind = 'q' and post_id = p_id and value = 1),
                         down = (select count(*) from votes where kind = 'q' and post_id = p_id and value = -1) where id = p_id;
  else
    update answers set up = (select count(*) from votes where kind = 'a' and post_id = p_id and value = 1),
                       down = (select count(*) from votes where kind = 'a' and post_id = p_id and value = -1) where id = p_id;
  end if;
end $$;

-- Report a post. 3 reports from different devices hide it until the owner checks it.
create or replace function public.report_post(p_kind text, p_id bigint, p_device text)
returns void language plpgsql security definer set search_path = public as $$
declare n int;
begin
  if p_kind not in ('q', 'a') or char_length(p_device) < 8 then raise exception 'bad_report'; end if;
  insert into reports (kind, post_id, device) values (p_kind, p_id, p_device) on conflict do nothing;
  select count(*) into n from reports where kind = p_kind and post_id = p_id;
  if p_kind = 'q' then
    update questions set reports = n, hidden = (hidden or n >= 3) where id = p_id;
  else
    update answers set reports = n, hidden = (hidden or n >= 3) where id = p_id;
  end if;
end $$;

revoke all on function public.ask_question(text, text, text, text, text, text), public.post_answer(bigint, text, text, text),
  public.cast_vote(text, bigint, text, int), public.report_post(text, bigint, text) from public;
grant execute on function public.ask_question(text, text, text, text, text, text), public.post_answer(bigint, text, text, text),
  public.cast_vote(text, bigint, text, int), public.report_post(text, bigint, text) to anon, authenticated;
