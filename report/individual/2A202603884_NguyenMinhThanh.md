**Sinh viên:** NguyenMinhThanh  
**MSSV:** 2A202603884

# Báo cáo Day 7

## Dữ liệu và benchmark

- Sinh viên: NguyenMinhThanh (MSSV 2A202603884)
- Nguồn Day 6: Student Handbook 2025, 32 trang, dữ liệu tạo cho lớp; benchmark hiện có 15 dev và 5 test câu có đáp án. Chưa có câu hỏi thiếu bằng chứng.
- Vector store Day 6: PostgreSQL + pgvector, bảng `strategy_chunks`, strategy B mặc định. Day 6 report ghi hit@1/evidence hit@3 đều 1.0, nhưng không ghi embedding model hoặc dimension. Dense Day 7 chưa chạy vì thiếu thông tin tương thích này.
- Agent model/key: chưa cấu hình; không có agent score.

- Nguồn, quyền sử dụng, số trang và số chunk:
- Vector store, embedding model, phiên bản và số chiều:
- Agent model, cách chạy và phân chia dev/test:
- Cách xác định câu có/thiếu evidence và tiêu chí chấm:

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| Cấu hình | Phương pháp/cấu hình | Giả thuyết | Split | Hit@1 | Evidence Hit@3 | Context evidence | Median retrieval time |
|---|---|---|---|---:|---:|---|---:|
| Baseline | TF-IDF, k=3 | Lexical baseline | dev | 5/15 | 5/15 | Top-3 chunk context: 5/15 | <1 ms |
| Dense | Day 6 pgvector, k=3 | Semantic retrieval improves paraphrase matching | dev | 14/15 | 15/15 | Top-3 chunk context: 15/15 | 322 ms |
| Method 3 | Hybrid RRF, k=3 | Combine lexical and dense ranks | dev | 13/15 | 15/15 | Top-3 chunk context: 15/15 | 302 ms |
| Improvement 1 | Hybrid RRF, k=3 | Test rank fusion across retrievers | dev | 13/15 | 15/15 | Top-3 chunk context: 15/15 | 302 ms |
| Improvement 2 | Dense, k=5 (report top-3 for comparable metric) | Larger candidate set could improve evidence coverage | dev | 14/15 | 15/15 | Top-3 context: 15/15 | 271 ms |
| Chosen | Dense, k=3 | Best Hit@1; same full Hit@3 as hybrid with fewer candidates | dev | 14/15 | 15/15 | 15/15 | 322 ms |
| Selected dense k=3 | Day 6 pgvector | Final dev choice | test | 5/5 | 5/5 | 5/5 top-3 |  (API-backed; precise cost unavailable) |
| Baseline TF-IDF k=3 | lexical | comparison baseline | test | 3/5 | 3/5 | 3/5 top-3 | <1 ms |

Một cấu hình có thể đồng thời là phương pháp mới và cải thiện; giải thích rõ. Báo `n/N` và tỷ lệ, ghi đơn vị thời gian/chi phí, so sánh test sau khi chốt. Nêu hai lỗi dev, nguyên nhân, cách thử và lý do chọn cấu hình:

## Agent và đánh giá

- Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|

- Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:
- Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:

## Thử thách nâng cao (nếu thực hiện)

- Tài liệu, nguồn, quyền sử dụng, số trang và phiên bản:
- Cách xử lý text, bảng, ảnh, biểu đồ; phạm vi index và phần chưa xử lý:
- Cách chia benchmark, schema evidence, model và cấu hình đã chốt trên dev:

| Nhóm test | Đạt / tổng | Tỷ lệ | Lỗi / nhận xét |
|---|---|---|---|
| Bảng | | | |
| Ảnh, sơ đồ | | | |
| Biểu đồ | | | |
| Multi-hop | | | |
| Text | | | |
| Thiếu bằng chứng | | | |
| **Toàn bộ** | | | |

- Trace, nhãn và evidence từng câu; thời gian, chi phí, lỗi hệ thống:
- Giới hạn, cách tái lập và đường dẫn benchmark:


## Tiến độ triển khai đến GUIDE.md §4

- Đã thêm adapter Day 6 dense, TF-IDF lexical, hybrid RRF và OpenAI-compatible tool-calling controller.
- Dev smoke run lexical thành công trên 15 câu; exact evidence+source+page xuất hiện trong top-k ở 5/15. Đây là kiểm tra retrieval thô; cần phân tích và không coi là answer quality.
- Day 6 index dùng `text-embedding-3-small`, 1536 chiều. Dense, TF-IDF và hybrid đã chạy trên cùng 15 câu dev. Agent dev và hai câu thiếu evidence đã chạy; cần nộp trace, nhãn chấm và test đánh giá sau khi chốt cấu hình.
- Lệnh dev lexical: `python starter/run_day7.py --day6 ../K5-L3-DAY06-NguyenMinhThanh-2A202603884-DataIngestionEngineering --split dev --method tfidf --output starter/results/tfidf-dev.json`.


## GUIDE §4: so sánh dev và quyết định cấu hình

- Điều kiện chung: cùng 32-page corpus, Day 6 strategy B index, benchmark 15 câu có evidence, filter từ benchmark, evidence hit yêu cầu source + page + exact quote; top-k=3 cho ba phương pháp.
- Trace: `starter/results/tfidf-dev.json`, `dense-dev.json`, `hybrid-dev.json`, `dense-k5-dev.json`. Retrieval cost là API-backed embeddings; tiền phí cụ thể chưa thu được từ usage telemetry.
- Chọn dense top-k=3 trên dev: Hit@1 14/15, Evidence Hit@3 15/15; hybrid đạt Evidence Hit@3 bằng nhau nhưng Hit@1 thấp hơn (13/15), TF-IDF thấp hơn nhiều. Dense k=5 không tăng Hit@3 so với k=3.
- Sau khi chốt dense trên dev, đã chạy baseline và cấu hình được chọn trên test: dense Hit@1 5/5, Evidence Hit@3 5/5; TF-IDF 3/5 và 3/5. Agent trả lời cả 5 câu answerable test, và từ chối đúng 2 câu unanswerable test mới. Cần audit thủ công câu trả lời/citation theo nguồn trước khi kết luận grounded score.


## GUIDE §5: trình bày và kết quả test

- Test retrieval trace: `starter/results/tfidf-test.json`, `starter/results/dense-selected-test.json`; dense đạt 5/5 top-1 và 5/5 top-3, baseline TF-IDF đạt 3/5.
- Agent test trace: `starter/results/agent-dense-test.json` (Q16–Q20, tất cả answered) và `starter/results/agent-unanswerable-test.json` (UTEST01–UTEST02, cả hai abstain). UTEST01 dùng 1 lượt tìm; UTEST02 dùng 4 lượt. Agent trace cần được giữ cùng báo cáo khi nộp; các file results bị ignore mặc định bởi Git.
- Ví dụ có bằng chứng: Q18 trả lời yêu cầu 120 credits, trừ trường hợp chương trình yêu cầu nhiều hơn, cite trang 17. Ví dụ thiếu evidence: UTEST01 hỏi địa chỉ nhà riêng của hiệu trưởng; agent abstain và không đưa citation. Lỗi: Q09 ở dev thêm suy luận về quyền cài phần mềm không được passage xác nhận.
- Giới hạn: Day 6 benchmark gốc có 20 câu answerable; bổ sung hai unanswerable dev và hai unanswerable test để đạt cấu trúc cơ bản. Human review đã xác nhận Q09 là lỗi; cần chấm đầy đủ grounded-answer/citation cho toàn bộ test theo rubric trước nộp.

## Thử thách nâng cao

Chưa thực hiện và không đủ điều kiện bonus. Corpus hiện có Student Handbook 2025, 32 trang, trong khi thử thách yêu cầu một tài liệu thực tế ít nhất 100 trang có bảng, ảnh và biểu đồ, retrieval cho nội dung trực quan, benchmark riêng tối thiểu 30 câu test và 18 câu dev theo phân bổ ADVANCED.md, audit từng câu và đạt ít nhất 90% test. Repo hiện không có corpus 100 trang, index trực quan, hay benchmark advanced phù hợp.
