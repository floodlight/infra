/****************************************************************
 *
 *        Copyright 2013, Big Switch Networks, Inc.
 *
 * Licensed under the Eclipse Public License, Version 1.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 *        http://www.eclipse.org/legal/epl-v10.html
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific
 * language governing permissions and limitations under the
 * License.
 *
 ****************************************************************/

/******************************************************************************
 *
 *  /utest/main.c
 *
 *  AIM Unit Testing
 *
 *****************************************************************************/
#include <AIM/aim_config.h>
#include <AIM/aim.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <AIM/aim_rl.h>
#include <AIM/aim_bitmap.h>

#define AIM_LOG_MODULE_NAME aim_utest
#include <AIM/aim_log.h>

AIM_LOG_STRUCT_DEFINE(1, 0xFFFFFFFF, NULL, 0);

extern int utest_list(void);


static void
test_logf(void* cookie, aim_log_flag_t flag, const char* str)
{
    printf("%s: cookie 0x%p, flag %s, msg %s",
           __func__, cookie, aim_log_flag_name(flag), str);
}

#define LOG_MACROS                               \
    log_desc(EMERG)                              \
    log_desc(ALERT)                              \
    log_desc(CRIT)                               \
    log_desc(ERROR)                              \
    log_desc(WARN)                               \
    log_desc(NOTICE)                             \
    log_desc(INFO)

void test_logging(void)
{
    aim_logf_set_all("testlogf", test_logf, NULL);

#define log_desc(level)                                                 \
    AIM_SYSLOG_##level("humanformat", "docstring", "syslog test %s", #level); \
    AIM_SYSLOG_RL_##level("humanformat", "docstring", NULL, 0, "syslog rl test %s", #level);

    LOG_MACROS;
#undef log_desc

    /* DEBUG has no docstring */
    AIM_SYSLOG_DEBUG("syslog test %s", "DEBUG");
    AIM_SYSLOG_RL_DEBUG(NULL, 0, "syslog rl test %s", "DEBUG");
}


int aim_main(int argc, char* argv[])
{
    int i;

    {
        const char* tstStrings[] = { "This", "is", "a", "complete", "sentence." };
        char* join = aim_strjoin(" ", tstStrings, AIM_ARRAYSIZE(tstStrings));
        if(strcmp(join, "This is a complete sentence.")) {
            printf("fail: join='%s'\n", join);
        }
        aim_free(join);
    }

    for(i = 0; i < argc; i++) {
        aim_printf(&aim_pvs_stdout, "arg%d: '%s'\n", i, argv[i]);
    }

    {
        /* Test data */
        char data[2500];
        memset(data, 0xFF, sizeof(data));
        aim_printf(&aim_pvs_stdout, "data is %{data}", data, sizeof(data));
    }

    {
        char* sdata = "DEADBEEFCAFE";
        char* data;
        int size;
        aim_sparse(&sdata, &aim_pvs_stdout, "{data}", &data, &size);
        aim_printf(&aim_pvs_stdout, "data is %{data}\n", data, size);
        aim_free(data);
    }

    utest_list();

    AIM_LOG_MSG("Should print 1-27");
    AIM_LOG_MSG("%d %d %d %d %d %d %d %d %d "
                "%d %d %d %d %d %d %d %d %d "
                "%d %d %d %d %d %d %d %d %d",
                1, 2, 3, 4, 5, 6, 7, 8, 9,
                10, 11, 12, 13, 14, 15, 16, 17, 18,
                19, 20, 21, 22, 23, 24, 25, 26, 27);


    aim_printf(&aim_pvs_stdout, "aim_pvs_stdout from %s:%d\n",
               __FILE__, __LINE__);


    {
        char c;
        aim_pvs_t* pvs = aim_pvs_buffer_create();
        aim_printf(pvs, "\nConsider ");
        aim_printf(pvs, "%s ", "the");
        aim_printf(pvs, "alphabet: ");
        for(c = 'A'; c <= 'Z'; c++) {
            aim_printf(pvs, "%c", c);
        }
        aim_printf(pvs, "\n");
        {
            char* s = aim_pvs_buffer_get(pvs);
            aim_printf(&aim_pvs_stdout, "first: %s", s);
            free(s);
            aim_printf(pvs, "(second)");
            s = aim_pvs_buffer_get(pvs);
            aim_printf(&aim_pvs_stdout, "second: %s", s);
            free(s);
            aim_pvs_buffer_reset(pvs);
            s = aim_pvs_buffer_get(pvs);
            free(s);
            aim_pvs_destroy(pvs);
        }
        {
            aim_ratelimiter_t rl;
            aim_ratelimiter_init(&rl, 10, 5, NULL);

            /* 5 (6?) tokens available at t=0 */
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) == 0);
            assert(aim_ratelimiter_limit(&rl, 0) < 0);

            /* Another token at t=10 */
            assert(aim_ratelimiter_limit(&rl, 10) == 0);
            assert(aim_ratelimiter_limit(&rl, 10) < 0);

            /* Nothing at t=15 */
            assert(aim_ratelimiter_limit(&rl, 15) < 0);

            /* 4 more tokens granted by t=50 */
            assert(aim_ratelimiter_limit(&rl, 50) == 0);
            assert(aim_ratelimiter_limit(&rl, 50) == 0);
            assert(aim_ratelimiter_limit(&rl, 50) == 0);
            assert(aim_ratelimiter_limit(&rl, 50) == 0);
            assert(aim_ratelimiter_limit(&rl, 50) < 0);
        }
        {
            aim_printf(&aim_pvs_stdout, "valgrind_status=%d\n",
                       aim_valgrind_status());
        }

        AIM_LOG_MSG("%{aim_error}", AIM_ERROR_PARAM);
    }

    {
        aim_pvs_t* pvs = aim_pvs_buffer_create();
        aim_pvs_logf(pvs, 0, "Buffer log: "
                     "The quick brown fox jumped over the lazy dogs.\n");
        {
            char* s = aim_pvs_buffer_get(pvs);
            aim_printf(&aim_pvs_stdout, "first: %s", s);
            free(s);
            aim_printf(pvs, "(second)");
            s = aim_pvs_buffer_get(pvs);
            aim_printf(&aim_pvs_stdout, "second: %s", s);
            free(s);
            aim_pvs_buffer_reset(pvs);
            assert(aim_pvs_buffer_size(pvs) == 0);
            s = aim_pvs_buffer_get(pvs);
            assert(s == NULL);
            free(s);
            aim_pvs_destroy(pvs);
        }
    }

    /* Test integer power of 2 utilities */
    {
       assert(!aim_is_pow2_u32(0));
       assert(aim_log2_u32(0) == 0);

       assert(aim_is_pow2_u32(1));
       assert(aim_log2_u32(1) == 0);

       assert(aim_is_pow2_u32(2));
       assert(aim_log2_u32(2) == 1);

       assert(!aim_is_pow2_u32(3));
       assert(aim_log2_u32(3) == 1);

       assert(aim_is_pow2_u32(4));
       assert(aim_log2_u32(4) == 2);

       assert(!aim_is_pow2_u32(5));
       assert(aim_log2_u32(5) == 2);

       assert(!aim_is_pow2_u32(6));
       assert(aim_log2_u32(6) == 2);

       assert(!aim_is_pow2_u32(7));
       assert(aim_log2_u32(7) == 2);

       assert(aim_is_pow2_u32(8));
       assert(aim_log2_u32(8) == 3);

       assert(!aim_is_pow2_u32(2147483647));
       assert(aim_log2_u32(2147483647) == 30);

       assert(aim_is_pow2_u32(2147483648));
       assert(aim_log2_u32(2147483648) == 31);

       assert(!aim_is_pow2_u32(4294967295));
       assert(aim_log2_u32(4294967295) == 31);
    }

    /* Test aim_dfstrdup() */
    {
        char* rv = aim_dfstrdup("%d %{bool} %{bool} %d %{8bits}", 1, 1, 0, 0, 0xA5);
        assert(!strcmp(rv, "1 True False 0 10100101"));
        aim_free(rv);
    }

    /* Test Bitmaps */
    {
        aim_bitmap_t* bmapZero = aim_bitmap_alloc(NULL, 128);
        aim_bitmap_t* bmapAll = aim_bitmap_alloc(NULL, 128);
        aim_bitmap_t* bmap1 = aim_bitmap_alloc(NULL, 128);
        aim_bitmap_t* bmap2 = aim_bitmap_alloc(NULL, 128);
        aim_bitmap_t* bmapTmp = aim_bitmap_alloc(NULL, 128);

        int i;
        for(i = 0; i < 128; i++) {
            AIM_BITMAP_SET(bmapAll, i);
            if(i & 1) {
                AIM_BITMAP_SET(bmap1, i);
            }
            else {
                AIM_BITMAP_SET(bmap2, i);
            }
        }

        assert(AIM_BITMAP_WORD_GET32(bmapZero, 0) == 0x0);
        assert(AIM_BITMAP_WORD_GET32(bmapZero, 1) == 0x0);
        assert(AIM_BITMAP_WORD_GET32(bmapZero, 2) == 0x0);
        assert(AIM_BITMAP_WORD_GET32(bmapZero, 3) == 0x0);

        assert(AIM_BITMAP_WORD_GET32(bmapAll, 0) == 0xFFFFFFFF);
        assert(AIM_BITMAP_WORD_GET32(bmapAll, 1) == 0xFFFFFFFF);
        assert(AIM_BITMAP_WORD_GET32(bmapAll, 2) == 0xFFFFFFFF);
        assert(AIM_BITMAP_WORD_GET32(bmapAll, 3) == 0xFFFFFFFF);

        assert(AIM_BITMAP_WORD_GET32(bmap1, 0) == 0xAAAAAAAA);
        assert(AIM_BITMAP_WORD_GET32(bmap1, 1) == 0xAAAAAAAA);
        assert(AIM_BITMAP_WORD_GET32(bmap1, 2) == 0xAAAAAAAA);
        assert(AIM_BITMAP_WORD_GET32(bmap1, 3) == 0xAAAAAAAA);

        assert(AIM_BITMAP_WORD_GET32(bmap2, 0) == 0x55555555);
        assert(AIM_BITMAP_WORD_GET32(bmap2, 1) == 0x55555555);
        assert(AIM_BITMAP_WORD_GET32(bmap2, 2) == 0x55555555);
        assert(AIM_BITMAP_WORD_GET32(bmap2, 3) == 0x55555555);

        /*
         * bmap1 & bmap2 == 0
         */
        AIM_BITMAP_ASSIGN(bmapTmp, bmap1);
        AIM_BITMAP_AND(bmapTmp, bmap2);
        assert(AIM_BITMAP_IS_EQ(bmapZero, bmapTmp));

        /*
         * bmap1 | bmap2 == all
         */
        AIM_BITMAP_ASSIGN(bmapTmp, bmap1);
        AIM_BITMAP_OR(bmapTmp, bmap2);
        assert(AIM_BITMAP_IS_EQ(bmapAll, bmapTmp));

        /*
         * bmap1 ^ bmap2 == all
         */
        AIM_BITMAP_ASSIGN(bmapTmp, bmap1);
        AIM_BITMAP_XOR(bmapTmp, bmap2);
        assert(AIM_BITMAP_IS_EQ(bmapAll, bmapTmp));

        /*
         * bmap1 ^ bmap1 == zero
         * bmap2 ^ bmap2 == zero
         */
        AIM_BITMAP_ASSIGN(bmapTmp, bmap1);
        AIM_BITMAP_XOR(bmapTmp, bmap1);
        assert(AIM_BITMAP_IS_EQ(bmapZero, bmapTmp));
        AIM_BITMAP_ASSIGN(bmapTmp, bmap2);
        AIM_BITMAP_XOR(bmapTmp, bmap2);
        assert(AIM_BITMAP_IS_EQ(bmapZero, bmapTmp));

        aim_bitmap_free(bmapZero);
        aim_bitmap_free(bmapAll);
        aim_bitmap_free(bmap1);
        aim_bitmap_free(bmap2);
        aim_bitmap_free(bmapTmp);
    }


    test_logging();

    {
        extern int aim_os_test(void);
        aim_os_test();
    }

    {
        char *sdata = "fe80::a:b:c:d";
        uint8_t edata[] = {
            0xfe, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x0a, 0x00, 0x0b, 0x00, 0x0c, 0x00, 0x0d,
        };
        uint8_t data[16];
        aim_sparse(&sdata, &aim_pvs_stdout, "{ipv6a}", data);
        assert(memcmp(data, edata, sizeof(edata)) == 0);

        aim_pvs_t *pvs = aim_pvs_buffer_create();
        aim_printf(pvs, "%{ipv6a}", data);
        char* s = aim_pvs_buffer_get(pvs);
        assert(strcmp(sdata, s) == 0);
        aim_pvs_destroy(pvs);
    }

    {
        char* sdata = "A\001B\002C\003D";
        char* rv = aim_pstrdup(sdata, '?');
        assert(!strcmp(rv, "A?B?C?D"));
        aim_free(rv);

        rv = aim_dfstrdup("%{pstr}", sdata, '.');
        assert(!strcmp(rv, "A.B.C.D"));
        aim_free(rv);
    }

    return 0;
}
