// '오늘의 물' — React Native(Expo) 버전
// PWA 버전(index.html)과 같은 기능을 휴대폰 앱 전용 부품으로 다시 만든 것.
// HTML의 <div> → <View>, 글자 → <Text>, <button> → <Pressable>
import { useCallback, useEffect, useState } from 'react';
import { AppState, Pressable, StyleSheet, Text, Vibration, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';

const GOAL = 2000;          // 하루 목표 (ml)
const CUP = 250;            // 한 잔 (ml)
const KEY = 'water-log';    // 휴대폰 안 저장소 이름: { "2026-11-24": 1250, ... }
const LAST = 'water-last';  // 마지막으로 '한 잔'을 누른 시각
const REMIND_MIN = 120;     // 이 시간(분)이 지나면 리마인더 카드를 보여 줌

const C = {
  bg: '#f2f7fd', card: '#ffffff', text: '#16324f', sub: '#5b7590',
  main: '#1c6dd0', mainDark: '#1559ab', light: '#d6e7fb', ok: '#1f9d6b',
};

// 휴대폰 시간 기준 날짜 글자 (예: 2026-11-24)
function dayKey(d) {
  const p = n => String(n).padStart(2, '0');
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
}
const won = n => n.toLocaleString('ko-KR');

export default function App() {
  const [tab, setTab] = useState('log');   // 'log' = 기록, 'stats' = 통계
  const [data, setData] = useState({});
  const [last, setLast] = useState(0);
  const [msg, setMsg] = useState('');
  const [now, setNow] = useState(Date.now());

  // 저장된 기록 읽기
  const load = useCallback(async () => {
    try {
      const raw = await AsyncStorage.getItem(KEY);
      setData(raw ? JSON.parse(raw) : {});
      setLast(Number(await AsyncStorage.getItem(LAST)) || 0);
    } catch (e) {}
    setNow(Date.now());
  }, []);

  useEffect(() => {
    load();
    // 앱을 다시 열 때마다 새로 읽기 (자정이 지났을 수도 있어서)
    const sub = AppState.addEventListener('change', s => { if (s === 'active') load(); });
    const timer = setInterval(() => setNow(Date.now()), 60000);  // 1분마다 리마인더 다시 계산
    return () => { sub.remove(); clearInterval(timer); };
  }, [load]);

  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(''), 2000);
    return () => clearTimeout(t);
  }, [msg]);

  async function save(next) {
    setData(next);
    try { await AsyncStorage.setItem(KEY, JSON.stringify(next)); } catch (e) {}
  }

  const today = dayKey(new Date(now));
  const ml = data[today] || 0;
  const pct = Math.round(ml / GOAL * 100);
  const left = Math.max(0, Math.ceil((GOAL - ml) / CUP));

  async function drink() {
    const next = { ...data, [today]: ml + CUP };
    await save(next);
    const t = Date.now();
    setLast(t); setNow(t);
    try { await AsyncStorage.setItem(LAST, String(t)); } catch (e) {}
    setMsg(ml < GOAL && ml + CUP >= GOAL ? '🎉 오늘 목표 달성!' : '좋아요! +250ml');
    Vibration.vibrate(30);
  }

  async function undo() {
    if (!ml) return;
    const next = { ...data, [today]: ml - CUP };
    if (next[today] <= 0) delete next[today];
    await save(next);
    setMsg('한 잔 되돌렸어요');
  }

  // 리마인더 문구 (없으면 null)
  let remind = null;
  if (ml < GOAL) {
    const lastIsToday = last && dayKey(new Date(last)) === today;
    if (ml === 0 && new Date(now).getHours() >= 9) {
      remind = ['☀️ 오늘 아직 한 잔도 안 마셨어요', '지금 한 잔으로 시작해요 · 남은 잔 ' + left + '잔'];
    } else if (lastIsToday) {
      const min = Math.floor((now - last) / 60000);
      if (min >= REMIND_MIN) {
        const h = Math.floor(min / 60), m = min % 60;
        remind = ['⏰ 마지막 한 잔에서 ' + h + '시간' + (m ? ' ' + m + '분' : '') + ' 지났어요',
                  '한 잔 어때요? · 남은 잔 ' + left + '잔'];
      }
    }
  }

  // 최근 7일 (6일 전 ~ 오늘)
  const names = ['일', '월', '화', '수', '목', '금', '토'];
  const week = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now); d.setDate(d.getDate() - i);
    week.push({ name: i === 0 ? '오늘' : names[d.getDay()], ml: data[dayKey(d)] || 0, today: i === 0 });
  }
  const top = Math.max(GOAL * 1.25, ...week.map(x => x.ml));
  const met = week.filter(x => x.ml >= GOAL).length;
  const total = week.reduce((s, x) => s + x.ml, 0);
  const CHART_H = 200;

  return (
    <View style={s.root}>
      <StatusBar style="dark" />
      <View style={s.main}>
        {tab === 'log' ? (
          <View>
            <Text style={s.h1}>💧 오늘의 물</Text>
            {remind && (
              <View style={s.remind}>
                <Text style={s.remindBig}>{remind[0]}</Text>
                <Text style={s.remindSmall}>{remind[1]}</Text>
              </View>
            )}
            <View style={s.card}>
              <Text style={s.amount}>{won(ml)}<Text style={s.amountSmall}> / 2,000ml</Text></Text>
              <View style={s.bar}>
                <View style={[s.barFill, { width: Math.min(pct, 100) + '%' }, ml >= GOAL && { backgroundColor: C.ok }]} />
              </View>
              <Text style={s.percent}>{pct}%</Text>
            </View>
            <Pressable onPress={drink} style={({ pressed }) => [s.drink, pressed && s.drinkPressed]}>
              <Text style={s.drinkText}>🥤 한 잔 마셨어요</Text>
              <Text style={s.drinkSmall}>+250ml</Text>
            </Pressable>
            <Pressable onPress={undo} disabled={!ml} style={[s.undo, !ml && { opacity: 0.4 }]}>
              <Text style={s.undoText}>↩ 되돌리기</Text>
            </Pressable>
            <Text style={s.msg}>{msg}</Text>
          </View>
        ) : (
          <View>
            <Text style={s.h1}>📊 최근 7일</Text>
            <View style={s.card}>
              <View style={[s.chart, { height: CHART_H }]}>
                <View style={[s.goalLine, { bottom: GOAL / top * CHART_H }]}>
                  <Text style={s.goalText}>목표 2,000ml</Text>
                </View>
                {week.map((x, i) => (
                  <View key={i} style={s.col}>
                    <Text style={s.colValue}>{x.ml ? won(x.ml) : ''}</Text>
                    <View style={[s.colBar, { height: Math.max(3, x.ml / top * (CHART_H - 20)) },
                      x.ml >= GOAL && { backgroundColor: C.ok },
                      x.today && { borderWidth: 3, borderColor: C.text }]} />
                  </View>
                ))}
              </View>
              <View style={s.days}>
                {week.map((x, i) => (
                  <Text key={i} style={[s.day, x.today && { color: C.main, fontWeight: '800' }]}>{x.name}</Text>
                ))}
              </View>
              <Text style={s.summary}>목표 채운 날: {met}일 / 7일</Text>
              <Text style={s.summarySmall}>7일 동안 모두 {won(total)}ml · 하루 평균 {won(Math.round(total / 7))}ml</Text>
            </View>
          </View>
        )}
      </View>

      {/* 아래 탭 */}
      <View style={s.nav}>
        {[['log', '💧', '기록'], ['stats', '📊', '통계']].map(([id, icon, label]) => (
          <Pressable key={id} style={s.navBtn} onPress={() => { setTab(id); load(); }}>
            <Text style={s.navIcon}>{icon}</Text>
            <Text style={[s.navText, tab === id && { color: C.main }]}>{label}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: C.bg },
  main: { flex: 1, paddingTop: 64, paddingHorizontal: 20 },
  h1: { fontSize: 22, fontWeight: '800', color: C.text, marginBottom: 18 },
  card: { backgroundColor: C.card, borderRadius: 20, padding: 20, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 10, shadowOffset: { width: 0, height: 2 } },
  remind: { backgroundColor: '#fff4d6', borderRadius: 16, padding: 14, marginBottom: 14 },
  remindBig: { color: '#6b4b00', fontSize: 16, fontWeight: '700' },
  remindSmall: { color: '#6b4b00', fontSize: 13, marginTop: 2 },
  amount: { textAlign: 'center', fontSize: 40, fontWeight: '800', color: C.text },
  amountSmall: { fontSize: 18, color: C.sub, fontWeight: '600' },
  bar: { height: 22, backgroundColor: C.light, borderRadius: 11, overflow: 'hidden', marginTop: 14, marginBottom: 8 },
  barFill: { height: '100%', backgroundColor: C.main, borderRadius: 11 },
  percent: { textAlign: 'center', color: C.sub, fontSize: 16 },
  drink: { marginTop: 26, marginBottom: 14, paddingVertical: 26, borderRadius: 24, backgroundColor: C.main, alignItems: 'center', borderBottomWidth: 6, borderBottomColor: C.mainDark },
  drinkPressed: { transform: [{ translateY: 4 }], borderBottomWidth: 2 },
  drinkText: { color: '#fff', fontSize: 24, fontWeight: '800' },
  drinkSmall: { color: '#fff', opacity: 0.85, fontSize: 15, fontWeight: '600', marginTop: 4 },
  undo: { alignSelf: 'center', paddingVertical: 12, paddingHorizontal: 22, borderWidth: 2, borderColor: C.light, borderRadius: 14 },
  undoText: { color: C.sub, fontSize: 16 },
  msg: { textAlign: 'center', minHeight: 24, marginTop: 14, color: C.ok, fontWeight: '700', fontSize: 16 },
  chart: { flexDirection: 'row', alignItems: 'flex-end', marginTop: 30, marginBottom: 8 },
  goalLine: { position: 'absolute', left: 0, right: 0, borderTopWidth: 2, borderStyle: 'dashed', borderColor: C.ok },
  goalText: { position: 'absolute', right: 0, top: -20, fontSize: 12, color: C.ok },
  col: { flex: 1, alignItems: 'center', justifyContent: 'flex-end', marginHorizontal: 4 },
  colValue: { fontSize: 10, color: C.sub, marginBottom: 3 },
  colBar: { width: '100%', backgroundColor: C.main, borderTopLeftRadius: 8, borderTopRightRadius: 8 },
  days: { flexDirection: 'row' },
  day: { flex: 1, textAlign: 'center', fontSize: 13, color: C.sub },
  summary: { marginTop: 20, fontSize: 20, fontWeight: '800', textAlign: 'center', color: C.text },
  summarySmall: { fontSize: 14, color: C.sub, textAlign: 'center', marginTop: 6 },
  nav: { flexDirection: 'row', backgroundColor: C.card, borderTopWidth: 1, borderTopColor: C.light, paddingBottom: 28 },
  navBtn: { flex: 1, alignItems: 'center', paddingTop: 12, paddingBottom: 6 },
  navIcon: { fontSize: 22 },
  navText: { fontSize: 15, fontWeight: '700', color: C.sub, marginTop: 2 },
});
