/**
 * 陽気軒 メニュー改訂検討シート 作成スクリプト
 *
 * 使い方：
 * 1. script.google.com で「新しいプロジェクト」を作成
 * 2. このファイルの中身を全部貼り付けて保存
 * 3. 上の関数選択で「buildMenuSheet」を選んで「実行」
 * 4. 初回は権限の許可を求められるので許可する
 * 5. 実行ログに表示されるURLを開く（マイドライブにも作成されます）
 *
 * 何度実行しても、そのたびに新しいスプレッドシートが作られます。
 * データ出典：youkiken/menu.json（2026-06時点）
 */

const MENU = {
  "updated": "2026-06",
  "globalNotes": [
    "ラーメン大盛りは平日無料／土日祝は＋¥200です。",
    "価格はすべて税込です。",
    "価格・メニューは変更になる場合があります。詳しくはお電話でご確認ください。"
  ],
  "setInfo": {
    "name": "ラーメンセット",
    "note": "お好きな麺類に プラス350円（※Bセットは揚げ餃子は出来ません）",
    "options": [
      "Aセット：半チャーハン",
      "Bセット：ジャンボ餃子3ケ",
      "Cセット：半カレー"
    ]
  },
  "days": {
    "weekday": {
      "label": "平日",
      "categories": [
        {
          "name": "ラーメン（醤油）",
          "note": "麺類大盛り無料",
          "items": [
            {
              "name": "ねぎラーメン",
              "price": 500
            },
            {
              "name": "中華そば",
              "price": 600
            },
            {
              "name": "陽気ラーメン",
              "price": 700,
              "tags": [
                "人気"
              ]
            },
            {
              "name": "チャーシューメン",
              "price": 900
            },
            {
              "name": "特製チャーシューメン",
              "price": 950
            },
            {
              "name": "あぶり焼きチャーシューメン",
              "price": 980
            },
            {
              "name": "全部のせラーメン",
              "price": 980
            },
            {
              "name": "ワンタンメン",
              "price": 750
            },
            {
              "name": "スタミナラーメン",
              "price": 950
            },
            {
              "name": "ニンニクラーメン",
              "price": 950
            },
            {
              "name": "チャーシュー3種ラーメン",
              "price": 980
            },
            {
              "name": "カレーラーメン",
              "price": 800
            },
            {
              "name": "マヨラーメン",
              "price": 800
            },
            {
              "name": "こくうまラーメン",
              "price": 750
            }
          ]
        },
        {
          "name": "ラーメン（味噌）",
          "items": [
            {
              "name": "味噌ラーメン",
              "price": 850
            },
            {
              "name": "辛味噌ラーメン",
              "price": 900
            },
            {
              "name": "味噌チャーシューメン",
              "price": 980
            },
            {
              "name": "味噌トマトチーズラーメン",
              "price": 950
            }
          ]
        },
        {
          "name": "ラーメン（塩）",
          "items": [
            {
              "name": "塩ねぎラーメン",
              "price": 550
            },
            {
              "name": "塩ラーメン",
              "price": 650
            },
            {
              "name": "タンメン",
              "price": 700
            },
            {
              "name": "野菜あんかけラーメン",
              "price": 850
            },
            {
              "name": "海鮮チャンポン",
              "price": 950
            },
            {
              "name": "えびそば（ラーメン）",
              "price": 950
            },
            {
              "name": "ギョーザラーメン",
              "price": 850
            },
            {
              "name": "玉子魚具あんかけラーメン",
              "price": 950
            }
          ]
        },
        {
          "name": "定食",
          "items": [
            {
              "name": "チャーシューエッグ",
              "price": 980
            },
            {
              "name": "チャーシュー玉子炒め",
              "price": 980
            },
            {
              "name": "野菜炒め",
              "price": 800
            },
            {
              "name": "肉野菜炒め",
              "price": 900
            },
            {
              "name": "レバニラ炒め",
              "price": 900
            },
            {
              "name": "玉子レバニラ炒め",
              "price": 880
            },
            {
              "name": "野菜レバニラ炒め",
              "price": 880
            },
            {
              "name": "スタミナ炒め",
              "price": 980
            },
            {
              "name": "ネギ玉炒め",
              "price": 750
            },
            {
              "name": "玉子きくらげ炒め（もつ）",
              "price": 750
            },
            {
              "name": "若鶏のから揚げ",
              "price": 980
            },
            {
              "name": "肉のかたまり",
              "price": 980
            },
            {
              "name": "豚かつ",
              "price": 980
            },
            {
              "name": "豚キムチ",
              "price": 980
            },
            {
              "name": "麻婆豆腐",
              "price": 900
            },
            {
              "name": "麻婆茄子",
              "price": 900
            },
            {
              "name": "カツ煮",
              "price": 900
            },
            {
              "name": "ジャンボギョーザ定食",
              "price": 950
            },
            {
              "name": "揚げギョーザ5個",
              "price": 980
            },
            {
              "name": "半ねぎラーメン",
              "price": 200
            },
            {
              "name": "まんぷく定食（ねぎラーメン＋半チャーハン＋餃子2個）",
              "price": 980
            }
          ]
        },
        {
          "name": "どんぶり",
          "note": "スープ・つけ物付",
          "items": [
            {
              "name": "玉子丼",
              "price": 500
            },
            {
              "name": "チャーシュー丼",
              "price": 800
            },
            {
              "name": "あぶり焼きチャーシュー丼",
              "price": 850
            },
            {
              "name": "中華丼",
              "price": 800
            },
            {
              "name": "かつ丼（玉子とじ）",
              "price": 800
            },
            {
              "name": "親子丼",
              "price": 800
            }
          ]
        },
        {
          "name": "チャーハン",
          "note": "スープ付",
          "items": [
            {
              "name": "チャーハン",
              "price": 650
            },
            {
              "name": "ネギ玉子チャーハン",
              "price": 500
            },
            {
              "name": "高菜チャーハン",
              "price": 600
            },
            {
              "name": "にんにくチャーハン",
              "price": 700
            },
            {
              "name": "スタミナチャーハン",
              "price": 750
            },
            {
              "name": "肉あんかけチャーハン",
              "price": 850
            },
            {
              "name": "ギョーザチャーハン",
              "price": 750
            },
            {
              "name": "海鮮あんかけチャーハン",
              "price": 850
            }
          ]
        },
        {
          "name": "ご飯類",
          "note": "スープ付",
          "items": [
            {
              "name": "カレーライス",
              "price": 650
            },
            {
              "name": "カツカレー",
              "price": 1000
            },
            {
              "name": "オムライス",
              "price": 900
            },
            {
              "name": "オムカレー",
              "price": 950
            },
            {
              "name": "ご飯類大盛り",
              "price": 200
            }
          ]
        },
        {
          "name": "麺類（焼きそば・冷やし）",
          "items": [
            {
              "name": "ソース焼きそば",
              "price": 650
            },
            {
              "name": "揚げ焼きそば",
              "price": 900
            },
            {
              "name": "塩焼きそば",
              "price": 650
            },
            {
              "name": "醤油焼きそば",
              "price": 650
            },
            {
              "name": "五目あんかけ焼きそば",
              "price": 950
            },
            {
              "name": "ざる中華",
              "price": 500
            },
            {
              "name": "冷やし中華（5月〜10月）",
              "price": 800
            },
            {
              "name": "冷やしラーメン",
              "price": 800
            },
            {
              "name": "替え玉",
              "price": 200
            }
          ]
        },
        {
          "name": "スープ",
          "items": [
            {
              "name": "玉子スープ",
              "price": 450
            },
            {
              "name": "にんにく玉子スープ",
              "price": 600
            },
            {
              "name": "ワンタンスープ",
              "price": 600
            },
            {
              "name": "たっぷり野菜の肉ワンタンスープ",
              "price": 650
            },
            {
              "name": "スープ大盛り",
              "price": 200
            }
          ]
        },
        {
          "name": "ライス",
          "note": "スープ・つけ物付",
          "items": [
            {
              "name": "ライス",
              "price": 350
            },
            {
              "name": "半ライス",
              "price": 250
            },
            {
              "name": "小ライス",
              "price": 200
            },
            {
              "name": "ニンニクライス",
              "price": 350
            },
            {
              "name": "バターライス",
              "price": 350
            },
            {
              "name": "鳥そぼろライス",
              "price": 350
            }
          ]
        },
        {
          "name": "ギョーザ",
          "note": "当店名物",
          "items": [
            {
              "name": "ジャンボギョーザ3個",
              "price": 360,
              "tags": [
                "名物"
              ]
            },
            {
              "name": "ジャンボギョーザ5個",
              "price": 600
            }
          ]
        },
        {
          "name": "トッピング",
          "items": [
            {
              "name": "昔ながらのチャーシュー3枚",
              "price": 250
            },
            {
              "name": "あぶり焼きチャーシュー1枚",
              "price": 200
            },
            {
              "name": "特製チャーシュー1枚",
              "price": 200
            },
            {
              "name": "コーン",
              "price": 150
            },
            {
              "name": "バター",
              "price": 150
            },
            {
              "name": "メンマ",
              "price": 150
            },
            {
              "name": "煮玉子",
              "price": 150
            },
            {
              "name": "生玉子",
              "price": 100
            }
          ]
        },
        {
          "name": "お飲み物",
          "note": "ソフトドリンクは店舗前の自動販売機をご利用ください",
          "items": [
            {
              "name": "ノンアルコールビール",
              "price": 450
            },
            {
              "name": "ビール（中ビン・キリン一番搾り）",
              "price": 650
            },
            {
              "name": "ビール（アサヒスーパードライ）",
              "price": 650
            },
            {
              "name": "サントリー角ハイボール",
              "price": 500
            },
            {
              "name": "チューハイ",
              "price": 450
            },
            {
              "name": "レモンサワー",
              "price": 450
            },
            {
              "name": "グレープフルーツサワー",
              "price": 450
            },
            {
              "name": "ウーロンハイ",
              "price": 450
            },
            {
              "name": "焼酎（甲類）ロック（グラス）",
              "price": 400
            },
            {
              "name": "焼酎（甲類）水割り（グラス）",
              "price": 400
            },
            {
              "name": "日本酒 聖徳（1合）",
              "price": 500
            }
          ]
        }
      ]
    },
    "weekend": {
      "label": "土日祝",
      "note": "土日祝は一部メニューを簡略してご提供しています。",
      "categories": [
        {
          "name": "ラーメン（醤油）",
          "note": "麺類大盛り＋¥200（土日祝）",
          "items": [
            {
              "name": "中華そば",
              "price": 600
            },
            {
              "name": "陽気ラーメン",
              "price": 700,
              "tags": [
                "人気"
              ]
            },
            {
              "name": "チャーシューメン",
              "price": 900
            },
            {
              "name": "特製チャーシューメン",
              "price": 950
            },
            {
              "name": "あぶり焼きチャーシューメン",
              "price": 980
            },
            {
              "name": "全部のせラーメン",
              "price": 980
            },
            {
              "name": "ワンタンメン",
              "price": 750
            },
            {
              "name": "スタミナラーメン",
              "price": 950
            },
            {
              "name": "ニンニクラーメン",
              "price": 950
            },
            {
              "name": "チャーシュー3種ラーメン",
              "price": 980
            },
            {
              "name": "カレーラーメン",
              "price": 800
            },
            {
              "name": "マヨラーメン",
              "price": 800
            },
            {
              "name": "こくうまラーメン",
              "price": 750
            }
          ]
        },
        {
          "name": "ラーメン（味噌）",
          "items": [
            {
              "name": "味噌ラーメン",
              "price": 850
            },
            {
              "name": "辛味噌ラーメン",
              "price": 900
            },
            {
              "name": "味噌チャーシューメン",
              "price": 980
            },
            {
              "name": "味噌トマトチーズラーメン",
              "price": 950
            }
          ]
        },
        {
          "name": "ラーメン（塩）",
          "items": [
            {
              "name": "塩ラーメン",
              "price": 650
            },
            {
              "name": "タンメン",
              "price": 700
            },
            {
              "name": "野菜あんかけラーメン",
              "price": 850
            },
            {
              "name": "海鮮チャンポン",
              "price": 950
            },
            {
              "name": "えびそば（ラーメン）",
              "price": 950
            },
            {
              "name": "ギョーザラーメン",
              "price": 850
            },
            {
              "name": "玉子魚具あんかけラーメン",
              "price": 950
            }
          ]
        },
        {
          "name": "単品",
          "items": [
            {
              "name": "おつまみチャーシュー",
              "price": 550
            },
            {
              "name": "チャーシューメンマ",
              "price": 450
            },
            {
              "name": "野菜炒め",
              "price": 550
            },
            {
              "name": "肉野菜炒め",
              "price": 700
            },
            {
              "name": "レバニラ炒め",
              "price": 700
            },
            {
              "name": "若鶏から揚げ",
              "price": 750
            }
          ]
        },
        {
          "name": "どんぶり",
          "note": "スープ・つけ物付",
          "items": [
            {
              "name": "玉子丼",
              "price": 500
            },
            {
              "name": "チャーシュー丼",
              "price": 800
            },
            {
              "name": "あぶり焼きチャーシュー丼",
              "price": 850
            },
            {
              "name": "中華丼",
              "price": 800
            },
            {
              "name": "かつ丼（玉子とじ）",
              "price": 800
            },
            {
              "name": "親子丼",
              "price": 800
            }
          ]
        },
        {
          "name": "チャーハン",
          "note": "スープ付",
          "items": [
            {
              "name": "チャーハン",
              "price": 650
            },
            {
              "name": "高菜チャーハン",
              "price": 600
            },
            {
              "name": "にんにくチャーハン",
              "price": 700
            },
            {
              "name": "スタミナチャーハン",
              "price": 750
            }
          ]
        },
        {
          "name": "ご飯類",
          "note": "スープ付",
          "items": [
            {
              "name": "カレーライス",
              "price": 650
            },
            {
              "name": "ご飯類大盛り",
              "price": 200
            }
          ]
        },
        {
          "name": "麺類（焼きそば）",
          "items": [
            {
              "name": "ソース焼きそば",
              "price": 650
            },
            {
              "name": "塩焼きそば",
              "price": 650
            },
            {
              "name": "醤油焼きそば",
              "price": 650
            },
            {
              "name": "替え玉",
              "price": 200
            }
          ]
        },
        {
          "name": "スープ",
          "items": [
            {
              "name": "玉子スープ",
              "price": 450
            },
            {
              "name": "にんにく玉子スープ",
              "price": 600
            },
            {
              "name": "ワンタンスープ",
              "price": 600
            },
            {
              "name": "たっぷり野菜の肉ワンタンスープ",
              "price": 650
            },
            {
              "name": "スープ大盛り",
              "price": 200
            }
          ]
        },
        {
          "name": "ライス",
          "note": "スープ・つけ物付",
          "items": [
            {
              "name": "ライス",
              "price": 350
            },
            {
              "name": "半ライス",
              "price": 250
            },
            {
              "name": "小ライス",
              "price": 200
            },
            {
              "name": "ニンニクライス",
              "price": 350
            },
            {
              "name": "バターライス",
              "price": 350
            },
            {
              "name": "鳥そぼろライス",
              "price": 350
            }
          ]
        },
        {
          "name": "ギョーザ",
          "note": "当店名物",
          "items": [
            {
              "name": "ジャンボギョーザ3個",
              "price": 360,
              "tags": [
                "名物"
              ]
            },
            {
              "name": "ジャンボギョーザ5個",
              "price": 600
            }
          ]
        },
        {
          "name": "トッピング",
          "items": [
            {
              "name": "昔ながらのチャーシュー3枚",
              "price": 250
            },
            {
              "name": "あぶり焼きチャーシュー1枚",
              "price": 200
            },
            {
              "name": "特製チャーシュー1枚",
              "price": 200
            },
            {
              "name": "コーン",
              "price": 150
            },
            {
              "name": "バター",
              "price": 150
            },
            {
              "name": "メンマ",
              "price": 150
            },
            {
              "name": "煮玉子",
              "price": 150
            },
            {
              "name": "生玉子",
              "price": 100
            }
          ]
        },
        {
          "name": "お飲み物",
          "note": "ソフトドリンクは店舗前の自動販売機をご利用ください",
          "items": [
            {
              "name": "ノンアルコールビール",
              "price": 450
            },
            {
              "name": "ビール（中ビン・キリン一番搾り）",
              "price": 650
            },
            {
              "name": "ビール（アサヒスーパードライ）",
              "price": 650
            },
            {
              "name": "サントリー角ハイボール",
              "price": 500
            },
            {
              "name": "チューハイ",
              "price": 450
            },
            {
              "name": "レモンサワー",
              "price": 450
            },
            {
              "name": "グレープフルーツサワー",
              "price": 450
            },
            {
              "name": "ウーロンハイ",
              "price": 450
            },
            {
              "name": "焼酎（甲類）ロック（グラス）",
              "price": 400
            },
            {
              "name": "焼酎（甲類）水割り（グラス）",
              "price": 400
            },
            {
              "name": "日本酒 聖徳（1合）",
              "price": 500
            }
          ]
        }
      ]
    }
  }
};

const STATUS_OPTIONS = ['継続', '削除', '新規追加', '値段変更'];
const HEADERS = ['カテゴリ', 'メニュー名', '現在の値段（円）', '改訂後の値段（円）', 'ステータス', '持ち帰り', '特盛', 'メモ'];
const COL_WIDTHS = [160, 300, 120, 140, 110, 80, 80, 260];
const NUM_COLS = HEADERS.length;
const EXTRA_ROWS = 30; // 新規追加用の空行

const COLOR_HEADER = '#8b4513';
const COLOR_CATEGORY = '#f5e6d3';
const COLOR_EDIT = '#fff9c4'; // 記入欄（薄い黄色）

function buildMenuSheet() {
  const ss = SpreadsheetApp.create('陽気軒 メニュー改訂検討');
  buildGuideTab(ss);
  buildDayTab(ss, 'weekday', '平日');
  buildDayTab(ss, 'weekend', '土日祝');
  const defaultSheet = ss.getSheetByName('シート1') || ss.getSheetByName('Sheet1');
  if (defaultSheet) ss.deleteSheet(defaultSheet);
  Logger.log('作成しました: ' + ss.getUrl());
}

function buildDayTab(ss, key, title) {
  const day = MENU.days[key];
  const sheet = ss.insertSheet(title);

  // ヘッダー
  sheet.getRange(1, 1, 1, NUM_COLS).setValues([HEADERS])
    .setBackground(COLOR_HEADER).setFontColor('#ffffff').setFontWeight('bold')
    .setHorizontalAlignment('center');
  sheet.setFrozenRows(1);
  COL_WIDTHS.forEach((w, i) => sheet.setColumnWidth(i + 1, w));

  // 行データを組み立て（カテゴリ見出し行＋商品行）
  const rows = [];        // 値
  const catRowIdx = [];   // カテゴリ見出し行の行番号（シート上）
  day.categories.forEach(cat => {
    let label = cat.name;
    if (cat.note) label += '　※' + cat.note;
    catRowIdx.push(rows.length + 2);
    rows.push([label, '', '', '', '', '', '', '']);
    cat.items.forEach(item => {
      let name = item.name;
      if (item.tags) name += '（' + item.tags.join('・') + '）';
      rows.push([cat.name, name, item.price, '', '継続', false, false, '']);
    });
  });

  sheet.getRange(2, 1, rows.length, NUM_COLS).setValues(rows);
  const dataEnd = rows.length + 1;   // 最終データ行
  const blankEnd = dataEnd + EXTRA_ROWS;

  // チェックボックス（持ち帰り F・特盛 G）
  // ※カテゴリ見出し行にもチェックボックスが乗らないよう、先に全体へ適用してから見出し行をクリアする
  const checkboxRule = SpreadsheetApp.newDataValidation().requireCheckbox().build();
  sheet.getRange(2, 6, blankEnd - 1, 2).setDataValidation(checkboxRule);
  catRowIdx.forEach(r => sheet.getRange(r, 6, 1, 2).clearDataValidations().clearContent());

  // カテゴリ見出し行の装飾
  catRowIdx.forEach(r => {
    sheet.getRange(r, 1, 1, NUM_COLS).setBackground(COLOR_CATEGORY).setFontWeight('bold');
    sheet.getRange(r, 1, 1, NUM_COLS).merge();
  });

  // 記入欄（改訂後の値段・ステータス・持ち帰り・特盛・メモ）＋新規追加用空行を黄色に
  sheet.getRange(2, 4, blankEnd - 1, 5).setBackground(COLOR_EDIT);
  sheet.getRange(dataEnd + 1, 1, EXTRA_ROWS, NUM_COLS).setBackground(COLOR_EDIT);
  catRowIdx.forEach(r => sheet.getRange(r, 1, 1, NUM_COLS).setBackground(COLOR_CATEGORY));

  // 罫線と数値書式
  sheet.getRange(1, 1, blankEnd, NUM_COLS).setBorder(true, true, true, true, true, true, '#cccccc', SpreadsheetApp.BorderStyle.SOLID);
  sheet.getRange(2, 3, blankEnd - 1, 2).setNumberFormat('#,##0');
  sheet.getRange(2, 6, blankEnd - 1, 2).setHorizontalAlignment('center');

  // ステータス列のプルダウン
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(STATUS_OPTIONS, true)
    .setAllowInvalid(false)
    .setHelpText('リストから選んでください（継続 / 削除 / 新規追加 / 値段変更）')
    .build();
  sheet.getRange(2, 5, blankEnd - 1, 1).setDataValidation(rule);

  // 末尾：特盛料金の記入欄＋セット・注記
  let r = blankEnd + 2;
  sheet.getRange(r, 1).setValue('【特盛の追加料金】＋');
  sheet.getRange(r, 2).setValue('円（ここに決めた金額を記入）').setFontColor('#666666');
  sheet.getRange(r, 1, 1, 2).setFontWeight('bold');
  sheet.getRange(r, 2).setFontWeight('normal');
  sheet.getRange(r, 1).setBackground(COLOR_EDIT);
  r += 2;

  const notes = [];
  const si = MENU.setInfo;
  if (si) notes.push('【' + si.name + '】' + si.note + '／' + si.options.join('、'));
  if (day.note) notes.push('【' + day.label + '】' + day.note);
  (MENU.globalNotes || []).forEach(n => notes.push('・' + n));
  notes.forEach((n, i) => {
    sheet.getRange(r + i, 1, 1, NUM_COLS).merge();
    sheet.getRange(r + i, 1).setValue(n).setFontColor('#666666').setFontSize(9);
  });
}

function buildGuideTab(ss) {
  const sheet = ss.insertSheet('使い方', 0);
  sheet.setColumnWidth(1, 800);
  const lines = [
    ['陽気軒 メニュー改訂 検討シート', 'title'],
    ['', ''],
    ['■ このシートの使い方', 'head'],
    ['・「平日」「土日祝」タブに現在の全メニューを転記してあります（出典：ホームページの menu.json、2026-06 時点）。', ''],
    ['・黄色のセルが記入欄です：改訂後の値段（円）／ステータス／持ち帰り／特盛／メモ', ''],
    ['・カテゴリ、メニュー名、現在の値段は現状の転記なので、基本は触らないでください。', ''],
    ['', ''],
    ['■ ステータス列（プルダウン）', 'head'],
    ['・継続：そのまま残す（初期値）', ''],
    ['・削除：メニューから外す', ''],
    ['・値段変更：残すが価格を変える → 「改訂後の値段」に新価格を記入', ''],
    ['・新規追加：新メニュー → 各タブ下部の黄色い空行に、カテゴリ・メニュー名・改訂後の値段を記入', ''],
    ['', ''],
    ['■ 持ち帰り・特盛列（チェックボックス）', 'head'],
    ['・持ち帰り：お持ち帰りできる品にチェック → メニュー表に「持」マークが付きます', ''],
    ['・特盛：特盛にできる品にチェック → メニュー表に「特盛」マークが付きます', ''],
    ['・特盛の追加料金は各タブ下部の記入欄に書いてください（メニュー表の凡例に載せます）', ''],
    ['', ''],
    ['■ 記入例', 'head'],
    ['　例1）陽気ラーメンを 700円 → 750円 にする場合：ステータス「値段変更」、改訂後の値段「750」', ''],
    ['　例2）新しく「冷やし坦々麺 900円」を加える場合：空行にカテゴリ「麺類（焼きそば・冷やし）」、メニュー名「冷やし坦々麺」、改訂後の値段「900」、ステータス「新規追加」', ''],
    ['　例3）チャーハンが持ち帰りOK・特盛OKなら：その行の「持ち帰り」「特盛」両方にチェック', ''],
    ['', ''],
    ['■ 検討が終わったら', 'head'],
    ['・このシートを元にホームページのメニュー（menu.json）と紙のメニュー表を更新します。', ''],
    ['・持ち帰り／特盛のチェックは、メニュー表上のマーク（凡例は右上に掲載）に反映されます。', ''],
  ];
  lines.forEach((l, i) => {
    const cell = sheet.getRange(i + 1, 1).setValue(l[0]);
    if (l[1] === 'title') cell.setFontWeight('bold').setFontSize(14);
    if (l[1] === 'head') cell.setFontWeight('bold');
  });
}
